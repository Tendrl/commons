import builtins
from etcd import EtcdResult
import importlib
import maps
import mock
from mock import patch
import time

from tendrl.commons.objects.cluster.atoms.stop_integration_services \
    import StopIntegrationServices
from tendrl.commons.objects.cluster import Cluster
from tendrl.commons.objects.job import Job


def test_constructor():
    StopIntegrationServices()


def nodes():
    obj = EtcdResult(
        **{
            'action': 'GET',
            'node': {
                'modifiedIndex': 190,
                'key': '/clusters/test_uuid/nodes/abc',
                'value': 'test'
            }
        }
    )
    return obj


def return_hash():
    obj = EtcdResult(
        **{
            'action': 'GET',
            'node': {
                'modifiedIndex': 190,
                'key': '/clusters/test_uuid/hash',
                'value': '13cf69912c5ee763caf4bf85bc7c8d7c'
            }
        }
    )
    return obj


def data():
    obj = EtcdResult(
        **{
            'action': 'GET',
            'node': {
                'modifiedIndex': 190,
                'key': '/clusters/test_uuid/data',
                'value': '{"current_job": {"status": "test_status",'
                          '"job_id": "5e2d4a84-fdb8-4386-a0c4-c25e2de17d3c",'
                          '"job_name": "test_job"},'
                          '"status": "",'
                          '"short_name": "test_name",'
                          '"volume_profiling_flag": "enable",'
                          '"conf_overrides": "",'
                          '"integration_id": "test_uuid",'
                          '"errors": "[]",'
                          '"node_configuration": "",'
                          '"locked_by": {},'
                          '"last_sync": "2018-06-13 07:31:13.145381+00:00",'
                          '"volume_profiling_state": "enabled",'
                          '"public_network": "",'
                          '"is_managed": "yes",'
                          '"node_identifier": "[]",'
                          '"cluster_network": "172.28.128.0/24"}'
            }
        }
    )
    return obj


def read(*args, **kwargs):
    if args:
        if args[0] == "/clusters/test_uuid/nodes":
            return nodes()
        elif args[0] == "/clusters/test_uuid/hash":
            return return_hash()
        elif args[0] == "clusters/test_uuid/data":
            return data()
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


def load_cluster(param):
    obj = maps.NamedDict()
    obj.short_name = "test_uuid"
    return obj


def init():
    setattr(builtins, "NS", maps.NamedDict())
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
    obj = StopIntegrationServices()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters["TendrlContext.integration_id"] = \
        "test_uuid"
    obj.parameters["job_id"] = "test_job_id"
    obj.parameters["flow_id"] = "test_flow_id"
    NS.publisher_id = "test"
    setattr(NS, "tendrl", maps.NamedDict())
    setattr(NS.tendrl, "objects", maps.NamedDict(Job=Job))
    setattr(NS, "config", maps.NamedDict(data={}))
    NS.tendrl.objects.NodeContext = mock.MagicMock()
    NS.tendrl.objects.Cluster = Cluster
    with patch.object(NS.tendrl.objects.Job, 'save', save):
        with patch.object(NS._int.client, 'read', read):
            with patch.object(
                    NS.tendrl.objects.Job, 'load', load_finished_job):
                with patch.object(
                        NS.tendrl.objects.Cluster,
                        'load',
                        load_cluster
                ):
                    ret_val = obj.run()
                    assert ret_val is True
    with patch.object(NS.tendrl.objects.Job, 'save', save):
        with patch.object(NS._int.client, 'read', read):
            with patch.object(
                    NS.tendrl.objects.Job, 'load', load_unfinished_job):
                with patch.object(time, 'sleep', sleep):
                    ret_val = obj.run()
                    assert ret_val is False
