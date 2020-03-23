import builtins
import etcd
import maps
from mock import patch

from tendrl.commons.objects.cluster.atoms.is_cluster_managed \
    import IsClusterManaged
from tendrl.commons.objects.cluster import Cluster


def test_constructor():
    IsClusterManaged()


def load_managed_cluster(*args):
    obj = maps.NamedDict()
    obj.integration_id = "13ced2a7-cd12-4063-bf6c-a8226b0789a0"
    obj.is_managed = "yes"
    return obj


def load_unmanaged_cluster(*args):
    obj = maps.NamedDict()
    obj.integration_id = "13ced2a7-cd12-4063-bf6c-a8226b0789a0"
    obj.is_managed = "no"
    return obj


def load_cluster_failed(*args):
    raise etcd.EtcdKeyNotFound


def test_run():
    obj = IsClusterManaged()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters["TendrlContext.integration_id"] = \
        "test_uuid"
    setattr(builtins, "NS", maps.NamedDict())
    setattr(NS, "tendrl", maps.NamedDict())
    setattr(NS.tendrl, "objects", maps.NamedDict())
    NS.tendrl.objects.Cluster = Cluster
    with patch.object(
        NS.tendrl.objects.Cluster,
        'load',
        load_managed_cluster
    ):
        ret_val = obj.run()
        assert ret_val is True
    with patch.object(
        NS.tendrl.objects.Cluster,
        'load',
        load_unmanaged_cluster
    ):
        ret_val = obj.run()
        assert ret_val is False
    with patch.object(
        NS.tendrl.objects.Cluster,
        'load',
        load_cluster_failed
    ):
        ret_val = obj.run()
        assert ret_val is True
