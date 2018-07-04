import __builtin__
import etcd
import importlib
import maps
import mock
from mock import patch
import pytest

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.expand_cluster import ExpandCluster
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS
from tendrl.commons.tests.fixtures.client import Client
from tendrl.commons.utils import etcd_utils


def read_failed(*args):
    if args[0]:
        if args[1] == 'nodes/TestNode/TendrlContext/integration_id':
            return maps.NamedDict(value="")
        else:
            return maps.NamedDict(value="failed")


def read_passed(*args):
    if args[0]:
        if args[1] == 'nodes/TestNode/TendrlContext/integration_id':
            return maps.NamedDict(value="")
        else:
            return maps.NamedDict(value="finished")


def get_parsed_defs():
    return {"namespace.tendrl": {"supported_sds": "gluster"}}


@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
@patch.object(etcd_utils, 'read')
@patch.object(node.NodeContext, 'load')
def init(patch_node_load,
         patch_etcd_utils_read,
         patch_get_node_id,
         patch_read,
         patch_client):
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
    patch_etcd_utils_read.return_value = maps.NamedDict(
        value='{"status": "UP",'
              '"pkey": "tendrl-node-test",'
              '"node_id": "test_node_id",'
              '"ipv4_addr": "test_ip",'
              '"tags": "[\\"my_tag\\"]",'
              '"sync_status": "done",'
              '"locked_by": "fd",'
              '"fqdn": "tendrl-node-test",'
              '"last_sync": "date"}')
    patch_node_load.return_value = node.NodeContext
    tendrlNS = TendrlNS()
    return tendrlNS


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.BaseFlow._execute_atom',
            mock.Mock(return_value=True))
@mock.patch('time.sleep',
            mock.Mock(return_value=True))
@mock.patch('tendrl.commons.objects.job.Job.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.save',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.utils.acquire_node_lock',
            mock.Mock(return_value=None))
@patch.object(etcd_utils, 'read')
def test_expand_cluster(patch_etcd_utils_read):
    expand_cluster = ExpandCluster()
    param = maps.NamedDict()
    param['TendrlContext.integration_id'] = None
    param['Node[]'] = []
    param["job_id"] = ""
    expand_cluster.parameters = param
    with pytest.raises(FlowExecutionFailedError):
        expand_cluster.run()
    param['TendrlContext.integration_id'] = "integration_id"
    param['TendrlContext.sds_name'] = "test_sds"
    tendrlNS = init()
    NS.compiled_definitions = tendrlNS.current_ns.definitions
    with pytest.raises(FlowExecutionFailedError):
        expand_cluster.run()
    param['TendrlContext.sds_name'] = "gluster"
    param['TendrlContext.cluster_name'] = 'test name'
    param["flow_id"] = "test_flow_id"
    param['Node[]'] = ['test_node']
    param["job_id"] = "test_id"
    param['TendrlContext.integration_id'] = None
    NS._int.client = importlib.import_module(
        "tendrl.commons.tests.fixtures.client").Client()
    NS.gluster_provisioner = importlib.import_module(
        "tendrl.commons.tests.fixtures.plugin").Plugin()
    NS.tendrl_context = maps.NamedDict(integration_id="")
    patch_etcd_utils_read.return_value = maps.NamedDict(
        value='{"status": "UP",'
              '"pkey": "tendrl-node-test",'
              '"node_id": "test_node_id",'
              '"ipv4_addr": "test_ip",'
              '"tags": "[\\"my_tag\\"]",'
              '"sync_status": "done",'
              '"locked_by": "fd",'
              '"fqdn": "tendrl-node-test",'
              '"last_sync": "date"}')
    with patch.object(Client, "read", read_failed):
        with pytest.raises(FlowExecutionFailedError):
            expand_cluster.run()
    param['TendrlContext.integration_id'] = "Test id"
    param['TendrlContext.sds_name'] = "gluster"
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = "Test id"
    with pytest.raises(FlowExecutionFailedError):
        expand_cluster.run()
