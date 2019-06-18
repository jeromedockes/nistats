from sklearn.utils import Bunch
import joblib
from nistats.datasets import fetch_bids_langloc_dataset
from nistats.first_level_model import first_level_models_from_bids
from nistats.reporting import xml_reports

MEMORY = joblib.Memory('/tmp/nistats_cache')


@MEMORY.cache
def get_model():
    data_dir, _ = fetch_bids_langloc_dataset()

    task_label = 'languagelocalizer'
    space_label = 'MNI152nonlin2009aAsym'
    (models, models_run_imgs,
     models_events, models_confounds) = first_level_models_from_bids(
        data_dir, task_label, space_label,
        img_filters=[('variant', 'smoothResamp')])

    model = models[0]
    model.signal_scaling = False
    activations = models_run_imgs[0][0]
    events = models_events[0][0]
    confounds = models_confounds[0][0]

    model.fit(activations, events, confounds)
    return model


model = get_model()

xml, html = xml_reports.make_report(
    model, ['language - string', 'string - language'])

xml = xml_reports.etree.tostring(
    xml, pretty_print=True,
    xml_declaration=True, encoding='utf-8').decode('utf-8')

html = xml_reports.etree.tostring(
    html, pretty_print=False,
    xml_declaration=True, encoding='utf-8').decode('utf-8')

with open('/tmp/report.xml', 'w') as f:
    f.write(xml)

with open('/tmp/report.xhtml', 'w') as f:
    f.write(html)

with open('/tmp/report.html', 'w') as f:
    f.write(html)

print('reports in /tmp/report.xml, /tmp/report.xhtml, /tmp/report.html')
