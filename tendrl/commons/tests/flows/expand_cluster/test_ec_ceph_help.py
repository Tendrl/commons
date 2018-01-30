import __builtin__
import etcd
import importlib
import json
import maps
import mock
from mock import patch


from tendrl.commons.flows.create_cluster import \
    ceph_help as create_ceph_help
from tendrl.commons.flows.expand_cluster import ceph_help
from tendrl.commons.tests.fixtures.client import Client


'''Dummy Functions'''


def read(*args, **kwargs):
    raise etcd.EtcdKeyNotFound


'''Unit Test Functions'''


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('socket.gethostbyaddr',
            mock.Mock(return_value=("Test_add", "")))
def test_expand_cluster():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    param = maps.NamedDict()
    setattr(NS, "_int", maps.NamedDict())
    NS._int.client = importlib.import_module(
        "tendrl.commons.tests.fixtures.client").Client()
    param["job_id"] = "test_id"
    param["flow_id"] = "test_flow_id"
    param['TendrlContext.integration_id'] = "test_integration_id"
    param['TendrlContext.cluster_id'] = ""
    param["TendrlContext.cluster_name"] = ""
    param["Cluster.cluster_network"] = ""
    param["Cluster.public_network"] = ""
    param["Cluster.node_configuration"] = {
        "test_node": maps.NamedDict(role="mon", provisioning_ip="test_ip")}
    NS.ceph_provisioner = importlib.import_module(
        "tendrl.commons.tests.fixtures.plugin").Plugin()
    with patch.object(Client, "read", return_value=maps.NamedDict(
        value="Test")):
        with patch.object(json, "loads", return_value={"mons": []}):
            ceph_help.expand_cluster(param)
    with patch.object(Client, "read", return_value=maps.NamedDict(
        value="Test")):
        with patch.object(json, "loads", return_value={"mons": []}):
            with patch.object(create_ceph_help, 'install_packages') as mock_fn:
                mock_fn.return_value = ['test_osd_ip'], []


@mock.patch('socket.gethostbyaddr',
            mock.Mock(return_value=("Test_add", "")))
def test_existing_mons():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    setattr(NS, "_int", maps.NamedDict())
    param = maps.NamedDict()
    NS._int.client = importlib.import_module(
        "tendrl.commons.tests.fixtures.client").Client()
    param['TendrlContext.integration_id'] = "test_integration_id"
    with patch.object(Client, "read", return_value=maps.NamedDict(
            value="Test")):
        with patch.object(json, "loads", return_value=maps.NamedDict(
            mons=[maps.NamedDict(addr="10:10:10:10")])):
            ceph_help.existing_mons(param)
