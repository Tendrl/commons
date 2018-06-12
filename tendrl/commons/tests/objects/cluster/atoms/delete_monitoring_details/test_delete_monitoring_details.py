import __builtin__
import importlib
import maps
from mock import patch

from tendrl.commons.objects.cluster.atoms.delete_monitoring_details \
    import DeleteMonitoringDetails
from tendrl.commons.objects.job import Job


def test_constructor():
    DeleteMonitoringDetails()


def save(*args):
    pass


def load_job(*args):
    return Job(job_id="uuid", status='finished')


def init():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    obj = importlib.import_module("tendrl.commons.tests.fixtures.client")
    NS._int.client = obj.Client()
    NS._int.wclient = obj.Client()


def test_run():
    init()
    obj = DeleteMonitoringDetails()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters["TendrlContext.integration_id"] = \
        "test_uuid"
    obj.parameters['job_id'] = "test_job_id"
    setattr(NS, "tendrl", maps.NamedDict())
    setattr(NS, "tendrl_context", maps.NamedDict())
    NS.tendrl_context['integration_id'] = "rete"
    setattr(NS.tendrl, "objects", maps.NamedDict(Job=Job))
    with patch.object(NS.tendrl.objects.Job, 'save', save):
        with patch.object(Job, 'load', load_job):
            obj.run()
