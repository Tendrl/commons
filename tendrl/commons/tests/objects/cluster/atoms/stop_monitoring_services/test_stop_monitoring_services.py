import __builtin__
from etcd import EtcdResult
import importlib
import maps
import mock
from mock import patch
import time

from tendrl.commons.objects.cluster.atoms.stop_monitoring_services \
    import StopMonitoringServices
from tendrl.commons.objects.job import Job


def test_constructor():
    StopMonitoringServices()


def nodes():
    obj = EtcdResult(
        **{
            u'action': u'GET',
            u'node': {
                u'modifiedIndex': 190,
                u'key': u'/clusters/test_uuid/nodes/abc',
                u'value': u'test'
            }
        }
    )
    return obj


def read(*args, **kwargs):
    if args:
        if args[0] == "/clusters/test_uuid/nodes":
            return nodes()
    else:
        return None


def save(*args):
    pass


def sleep(*args):
    pass


def load_finished_job(*args):
    return Job(job_id="uuid", status='finished')


def load_unfinished_job(*args):
    return Job(job_id="uuid", status='in_progress')


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


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    init()
    obj = StopMonitoringServices()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters["TendrlContext.integration_id"] = \
        "test_uuid"
    obj.parameters["job_id"] = "test_job_id"
    obj.parameters["flow_id"] = "test_flow_id"
    NS.publisher_id = "test"
    setattr(NS, "tendrl", maps.NamedDict())
    setattr(NS.tendrl, "objects", maps.NamedDict(Job=Job))
    with patch.object(NS.tendrl.objects.Job, 'save', save):
        with patch.object(NS._int.client, 'read', read):
            with patch.object(Job, 'load', load_finished_job):
                ret_val = obj.run()
                assert ret_val is True
    with patch.object(NS.tendrl.objects.Job, 'save', save):
        with patch.object(NS._int.client, 'read', read):
            with patch.object(
                    NS.tendrl.objects.Job, 'load', load_unfinished_job):
                with patch.object(time, 'sleep', sleep):
                    ret_val = obj.run()
                    assert ret_val is False
