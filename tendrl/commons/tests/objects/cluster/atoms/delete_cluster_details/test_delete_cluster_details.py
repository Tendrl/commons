import __builtin__
from etcd import EtcdResult
import importlib
import maps
from mock import patch

from tendrl.commons.objects.cluster.atoms.delete_cluster_details \
    import DeleteClusterDetails
from tendrl.commons.objects.cluster import Cluster


def nodes():
    obj = EtcdResult(**{u'action': u'get',
                        u'node': {u'createdIndex': 20521,
                                  u'key': u'/clusters/test_uuid/nodes',
                                  u'modifiedIndex': 20521,
                                  u'nodes': [{u'createdIndex': 20521,
                                              u'modifiedIndex': 20521,
                                              u'key': u'/clusters/test_uuid'
                                                      u'/nodes/test_node1',
                                              u'dir': True}],
                                  u'dir': True}}
                     )
    return obj


def cluster_alerts():
    obj = EtcdResult(**{u'action': u'get',
                        u'node': {u'createdIndex': 20521,
                                  u'key': u'/clusters/test_uuid/nodes',
                                  u'modifiedIndex': 20521,
                                  u'nodes': [{u'createdIndex': 20521,
                                              u'modifiedIndex': 20521,
                                              u'key': u'/clusters/test_uuid'
                                                      u'/nodes/test_node1',
                                              u'dir': True}
                                             ],
                                  u'dir': True}}
                     )
    return obj


def node_alerts():
    obj = EtcdResult(**{u'action': u'get',
                        u'node': {u'createdIndex': 82420,
                                  u'key': u'/alerting/nodes/test_node1',
                                  u'modifiedIndex': 82420,
                                  u'nodes': [{u'createdIndex': 82420,
                                              u'modifiedIndex': 82420,
                                              u'expiration': u'2018-06-14T15:'
                                                             u'02:54.34944151'
                                                             u'4Z',
                                              u'key': u'/alerting/nodes/'
                                                      u'test_node1/alert1',
                                              u'ttl': 172684,
                                              u'dir': True}],
                                  u'dir': True}}
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
        if args[0] == "/alerting/clusters/test_uuid":
            return cluster_alerts()
        if args[0] == "/alerting/nodes/test_node1":
            return node_alerts()
        if args[0] == "/indexes/tags/gluster/server":
            return gluster_servers()
    else:
        return None


def test_constructor():
    DeleteClusterDetails()


def delete(*args, **kwargs):
    pass


def load_cluster(param):
    obj = maps.NamedDict()
    obj.short_name = "test_uuid"
    obj.save = save_cluster
    return obj


def save_cluster(*args, **kwargs):
    return True


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
    obj.parameters['job_id'] = "test_job_id"
    obj.parameters['flow_id'] = "test_flow_id"
    setattr(NS, "tendrl", maps.NamedDict())
    setattr(NS, "tendrl_context", maps.NamedDict())
    NS.tendrl_context['integration_id'] = "test_uuid"
    setattr(NS.tendrl, "objects", maps.NamedDict())
    NS.tendrl.objects.Cluster = Cluster
    NS.publisher_id = "publisher"
    with patch.object(NS._int.client, 'read', read):
        with patch.object(NS._int.wclient, 'delete', delete):
            with patch.object(
                NS.tendrl.objects.Cluster,
                'load',
                load_cluster
            ):
                with patch.object(NS.tendrl.objects.Cluster,
                                  'save',
                                  save_cluster):
                    obj.run()
