import __builtin__
import etcd
import maps
import mock
from mock import patch

from tendrl.commons.objects import BaseObject
from tendrl.commons.objects.cluster.atoms.set_cluster_unmanaged \
    import SetClusterUnmanaged
from tendrl.commons.objects.cluster import Cluster


def test_constructor():
    SetClusterUnmanaged()


def load_cluster(param):
    obj = Cluster()
    obj.integration_id = "13ced2a7-cd12-4063-bf6c-a8226b0789a0"
    return obj


def load_cluster_failed(param):
    raise etcd.EtcdKeyNotFound


def save(param):
    pass


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    obj = SetClusterUnmanaged()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters["TendrlContext.integration_id"] = \
        "test_uuid"
    obj.parameters["job_id"] = "test_job_id"
    obj.parameters["flow_id"] = "test_flow_id"
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "tendrl", maps.NamedDict())
    setattr(NS.tendrl, "objects", maps.NamedDict())
    NS.tendrl.objects.Cluster = Cluster

    with patch.object(
        NS.tendrl.objects.Cluster,
        'load',
        load_cluster
    ):
        with patch.object(BaseObject, 'save', save):
            ret_val = obj.run()
            assert ret_val is True
    with patch.object(
        NS.tendrl.objects.Cluster,
        'load',
        load_cluster_failed
    ):
        ret_val = obj.run()
        assert ret_val is False
