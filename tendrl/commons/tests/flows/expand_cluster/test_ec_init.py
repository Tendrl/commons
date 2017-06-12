import importlib
import pytest
import etcd
import __builtin__
import mock
from mock import patch
import maps
from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects.job import Job
from tendrl.commons.tests.fixtures.client import Client
from tendrl.commons.flows.create_cluster import \
    utils as create_cluster_utils
from tendrl.commons.flows.expand_cluster import ceph_help
from tendrl.commons.flows.expand_cluster import ExpandCluster
from tendrl.commons.flows.expand_cluster import gluster_help
from tendrl.commons import TendrlNS
import tendrl.commons.objects.node_context as node


'''Dummy Functions'''


def read_failed(*args,**kwargs):
    if args[0]:
        if args[1] == 'nodes/TestNode/TendrlContext/integration_id':
            return maps.NamedDict(value = "")
        else:
            return maps.NamedDict(value = "failed")


def read_passed(*args,**kwargs):
    if args[0]:
        if args[1] == 'nodes/TestNode/TendrlContext/integration_id':
            return maps.NamedDict(value = "")
        else:
            return maps.NamedDict(value = "finished")


'''Unit Test Cases'''


@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
def init(patch_get_node_id, patch_read, patch_client):
    patch_get_node_id.return_value = 1
    patch_read.return_value = etcd.Client()
    patch_client.return_value = etcd.Client()
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS._int.wclient = etcd.Client(**NS._int.etcd_kwargs)
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    NS.publisher_id = "node_context"
    NS.config.data['etcd_port'] = 8085
    NS.config.data['etcd_connection'] = "Test Connection"
    tendrlNS = TendrlNS()
    return tendrlNS


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.BaseFlow._execute_atom',
            mock.Mock(return_value=True))
@mock.patch('gevent.sleep',
            mock.Mock(return_value=True))
@mock.patch('tendrl.commons.objects.job.Job.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.save',
            mock.Mock(return_value=None))
def test_expand_cluster():
    expand_cluster = ExpandCluster()
    param = maps.NamedDict()
    param['TendrlContext.integration_id'] = None
    expand_cluster.parameters = param
    with pytest.raises(FlowExecutionFailedError):
        expand_cluster.run()
    param['TendrlContext.integration_id'] = "integration_id"
    param['TendrlContext.sds_name'] = "test_sds"
    tendrlNS = init()
    NS.compiled_definitions = tendrlNS.current_ns.definitions
    with pytest.raises(FlowExecutionFailedError):
        expand_cluster.run()
    param['TendrlContext.sds_name'] = "ceph"
    param['TendrlContext.cluster_name'] = 'test name'
    param["flow_id"] = "test_flow_id"
    param['Node[]'] = ['test_node']
    
    param["job_id"] = "test_id"
    NS._int.client = importlib.import_module("tendrl.commons.tests.fixtures.client").Client()
    NS.ceph_provisioner = importlib.import_module("tendrl.commons.tests.fixtures.plugin").Plugin()
    NS.tendrl_context = maps.NamedDict(integration_id = "")
    with patch.object(Client,"read",read_failed) as mock_read:
        with pytest.raises(FlowExecutionFailedError):
            expand_cluster.run()
    param["Cluster.node_configuration"] = {"test_node": maps.NamedDict(role="mon",provisioning_ip="test_ip")}
    param['TendrlContext.cluster_id'] = ""
    param["TendrlContext.cluster_name"] = ""
    param["Cluster.cluster_network"] = ""
    param["Cluster.public_network"] = ""
    with patch.object(Client,"read",read_passed) as mock_read:
        with patch.object(ceph_help,'expand_cluster',return_value = True):
            expand_cluster.run()
    param['TendrlContext.sds_name'] = "gluster"
    with patch.object(Client,"read",read_failed) as mock_read:
        with pytest.raises(KeyError):
            expand_cluster.run()
