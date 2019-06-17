import io

from lxml import etree
from lxml.builder import ElementMaker

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt


REPORT = b"""<?xml version="1.0" encoding="UTF-8"?>
<nistats:report xmlns:nistats="https://nistats.github.io">
    <nistats:title></nistats:title>
    <nistats:model_info></nistats:model_info>
    <nistats:design_matrices></nistats:design_matrices>
    <nistats:contrast_list></nistats:contrast_list>
</nistats:report>
"""

XSLT = b"""<?xml version="1.0" encoding="UTF-8"?>
<xsl:transform version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:nistats="https://nistats.github.io" >
<xsl:output method="xhtml" encoding="UTF-8" />

<xsl:template match="/">
<html>
<head>
<title><xsl:value-of select="/nistats:report/nistats:title/text()"/></title>
<meta charset="UTF-8"/>
</head>
<body>
<xsl:apply-templates/>
</body>
</html>
</xsl:template>

<xsl:template match="nistats:title">
    <h1><xsl:value-of select="text()"/></h1>
</xsl:template>

<xsl:template match="nistats:model_parameters">
<div>
<h2>model parameters</h2>
<xsl:for-each select="nistats:model_parameter">
    <span>
<xsl:attribute name="title">description: "<xsl:value-of
    select="nistats:parameter_description"/>"
</xsl:attribute>
    <xsl:value-of select="nistats:parameter_name"/> : <xsl:value-of
        select="nistats:parameter_value"/>
</span>
    <br/>
</xsl:for-each>
</div>
</xsl:template>

<xsl:template match="nistats:design_matrices">
<h2>Design matrices</h2>
<xsl:copy-of select="table"/>
</xsl:template>

<xsl:template match="nistats:contrast">
<div>
<h2>Contrast: <xsl:value-of select="nistats:contrast_name"/></h2>
<p>statistic type: <xsl:value-of select="nistats:statistic_type"/></p>
<xsl:copy-of select="nistats:stat_map_plot"/>
</div>
</xsl:template>

</xsl:transform>
"""

NSMAP = {'nistats': 'https://nistats.github.io'}
NS = ElementMaker(namespace="https://nistats.github.io",
                  nsmap={'nistats': "https://nistats.github.io"})


def fig_to_svg(fig=None):
    if fig is None:
        fig = plt.gcf()
    buf = io.BytesIO()
    try:
        fig.savefig(buf, format='svg')
        buf.seek(0)
        svg = etree.fromstring(buf.read())
    finally:
        buf.close()
    return svg


def report_contrast(model, contrast):
    fig = plt.figure()
    plt.scatter(*np.random.randn(2, 30))
    img = fig_to_svg(fig)
    plt.close('all')
    return NS.contrast(
        NS.contrast_name(contrast),
        NS.statistic_type("Z"),
        NS.stat_map_plot(img))


def report_model_params(model):
    parts = [NS.model_parameter(NS.parameter_name(k),
                                NS.parameter_value(str(v)),
                                NS.parameter_description(k))
             for (k, v) in model.items()]
    return NS.model_parameters(*parts)


def report_design_matrices(model):
    design = pd.DataFrame(np.random.randn(4, 3), columns=list('ABC'))
    table = design.to_html()
    return etree.XML(table)


def make_report(model, contrasts):
    # stat_map = model.compute_contrast(contrast)
    tree = etree.fromstring(REPORT)
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
    transform = etree.XSLT(etree.XML(XSLT))
    return tree, transform(tree)
