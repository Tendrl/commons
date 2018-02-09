import __builtin__
from etcd import EtcdResult
import importlib
import maps
from mock import patch

from tendrl.commons.objects.cluster.atoms.delete_cluster_details \
    import DeleteClusterDetails
from tendrl.commons.objects.cluster_tendrl_context \
    import ClusterTendrlContext


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


def cluster_alerts():
    obj = EtcdResult(
        **{
            u'action': u'GET',
            u'node': {
                u'modifiedIndex': 190,
                u'key': u'/alerting/clusters/test_uuid',
                u'value': u'test'
            }
        }
    )
    return obj


def node_alerts():
    obj = EtcdResult(
        **{
            u'action': u'GET',
            u'node': {
                u'modifiedIndex': 190,
                u'key': u'/alerting/nodes/test_uuid',
                u'value': u'test'
            }
        }
    )
    return obj


def gluster_servers():
    obj = EtcdResult(
        **{
            u'action': u'GET',
            u'node': {
                u'modifiedIndex': 190,
                u'key': u'/indexes/tags/gluster/server',
                u'value': u'["abc", "mno"]'
            }
        }
    )
    return obj


def read(*args, **kwargs):
    if args:
        if args[0] == "/clusters/test_uuid/nodes":
            return nodes()
        if args[0] == "/alerting/clusters":
            return cluster_alerts()
        if args[0] == "/alerting/nodes":
            return node_alerts()
        if args[0] == "/indexes/tags/gluster/server":
            return gluster_servers()
    else:
        return None


def test_constructor():
    DeleteClusterDetails()


def delete(*args, **kwargs):
    pass


def load_cluster_tendrl_context(param):
    obj = maps.NamedDict()
    obj.integration_id = "13ced2a7-cd12-4063-bf6c-a8226b0789a0"
    obj.cluster_id = "test"
    return obj


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
    obj = DeleteClusterDetails()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters["TendrlContext.integration_id"] = \
        "test_uuid"
    setattr(NS, "tendrl", maps.NamedDict())
    setattr(NS, "tendrl_context", maps.NamedDict())
    NS.tendrl_context['integration_id'] = "rete"
    setattr(NS.tendrl, "objects", maps.NamedDict())
    NS.tendrl.objects.ClusterTendrlContext = ClusterTendrlContext
    with patch.object(NS._int.client, 'read', read):
        with patch.object(NS._int.client, 'delete', delete):
            with patch.object(
                NS.tendrl.objects.ClusterTendrlContext,
                'load',
                load_cluster_tendrl_context
            ):
                obj.run()
