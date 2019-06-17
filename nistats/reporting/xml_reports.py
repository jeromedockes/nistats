import io
import pathlib
import random

from lxml import etree
from lxml.builder import ElementMaker

from nilearn import plotting, input_data, datasets
from nistats.thresholding import fdr_threshold
from matplotlib import pyplot as plt
import matplotlib as mpl

NSMAP = {'nistats': 'https://nistats.github.io'}
NS = ElementMaker(namespace="https://nistats.github.io",
                  nsmap={'nistats': "https://nistats.github.io"})


def get_report_template():
    template_path = str(pathlib.Path(__file__).parent / 'report_template.xml')
    return etree.parse(template_path)


def get_stylesheet():
    xsl_path = str(pathlib.Path(__file__).parent / 'report_to_html.xsl')
    return etree.XSLT(etree.parse(xsl_path))


def get_masker(mask_img=None):
    if mask_img is None:
        mask_img = datasets.load_mni152_brain_mask()
    return input_data.NiftiMasker(mask_img).fit([])


def fig_to_svg(fig=None, fig_id=None):
    if fig_id is None:
        fig_id = random.randint(0, int(1e6))
    fig_id = str(fig_id)
    if fig is None:
        fig = plt.gcf()
    buf = io.BytesIO()
    try:
        with mpl.rc_context(rc={'svg.fonttype': 'none'}):
            fig.savefig(buf, format='svg')
            buf.seek(0)
            svg = etree.fromstring(buf.read())
    finally:
        buf.close()
    return svg


def report_contrast(model, contrast):
    stat_map = model.compute_contrast(contrast)
    masker = get_masker()
    data = masker.transform(stat_map)
    threshold = fdr_threshold(data, .05)
    stat_map = masker.inverse_transform(data)
    plotting.plot_stat_map(stat_map, threshold=threshold)
    img = fig_to_svg()
    plt.close('all')
    return NS.contrast(
        NS.contrast_name(contrast),
        NS.statistic_type("Z"),
        NS.stat_map_plot(img))


def report_model_params(model):
    parts = [NS.model_parameter(NS.parameter_name(k),
                                NS.parameter_value(str(v)),
                                NS.parameter_description(k))
             for (k, v) in model.__dict__.items()
             if not k.endswith('_')]
    return NS.model_parameters(*parts)


def report_design_matrices(model):
    design = model.design_matrices_[0]
    table = design.to_html()
    return etree.XML(table)


def make_report(model, contrasts):
    tree = get_report_template()
    tree.xpath(
        'nistats:title', namespaces=NSMAP)[0].text = 'Nistats Report'
    tree.xpath(
        'nistats:model_info', namespaces=NSMAP)[0].append(
            report_model_params(model))
    tree.xpath(
        'nistats:design_matrices', namespaces=NSMAP)[0].append(
            report_design_matrices(model))
    for contrast in contrasts:
        tree.xpath('nistats:contrast_list', namespaces=NSMAP
                   )[0].append(report_contrast(model, contrast))
    transform = get_stylesheet()
    return tree, transform(tree)
