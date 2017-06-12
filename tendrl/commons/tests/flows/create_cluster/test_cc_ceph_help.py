import maps
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.create_cluster import ceph_help
import mock
import etcd
import gevent
from mock import patch
import __builtin__
import importlib
import pytest
from tendrl.commons.tests.fixtures.client import Client


'''Dummy Functions'''


def read(*args,**kwargs):
    raise etcd.EtcdKeyNotFound


'''Test Functions'''


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('gevent.sleep',
            mock.Mock(return_value=True))
def test_create_ceph():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    param = maps.NamedDict()
    param["job_id"] = "test_id"
    param["flow_id"] = "test_flow_id"
    param['TendrlContext.integration_id'] = "test_integration_id"
    param['TendrlContext.cluster_id'] = ""
    param["TendrlContext.cluster_name"] = ""
    param["Cluster.cluster_network"] = ""
    param["Cluster.public_network"] = ""
    param["Cluster.node_configuration"] = {"test_node": maps.NamedDict(role="mon",provisioning_ip="test_ip")}
    NS.ceph_provisioner = importlib.import_module("tendrl.commons.tests.fixtures.plugin").Plugin()
    ceph_help.create_ceph(param)


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('gevent.sleep',
            mock.Mock(return_value=True))
def test_install_packages():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    param = maps.NamedDict()
    param["job_id"] = "test_id"
    param["flow_id"] = "test_flow_id"
    param["Cluster.node_configuration"] = {"test_node": maps.NamedDict(role="osd",provisioning_ip="test_ip")}
    NS.ceph_provisioner = importlib.import_module("tendrl.commons.tests.fixtures.plugin").Plugin()
    ceph_help.install_packages(param)
    param["Cluster.node_configuration"] = {"test_node": maps.NamedDict(role="test_role",provisioning_ip="test_ip")}
    ceph_help.install_packages(param)


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('gevent.sleep',
            mock.Mock(return_value=True))
@patch.object(etcd, "Client")
def test_create_mons(patch_client):
    patch_client.return_value = etcd.Client()
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.wclient = etcd.Client(**NS._int.etcd_kwargs)
    param = maps.NamedDict()
    param["job_id"] = "test_id"
    param["flow_id"] = "test_flow_id"
    param['TendrlContext.integration_id'] = "test_integration_id"
    param['TendrlContext.cluster_id'] = ""
    param["TendrlContext.cluster_name"] = ""
    param["Cluster.cluster_network"] = ""
    param["Cluster.public_network"] = ""
    param['create_mon_secret'] = True
    NS.ceph_provisioner = importlib.import_module("tendrl.commons.tests.fixtures.plugin").Plugin()
    with patch.object(etcd.Client,"write",return_value = True):
        ceph_help.create_mons(param,["test_mon_ip"])


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('gevent.sleep',
            mock.Mock(return_value=True))
@patch.object(etcd, "Client")
def test_create_osds(patch_client):
    patch_client.return_value = etcd.Client()
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = importlib.import_module("tendrl.commons.tests.fixtures.client").Client()
    param = maps.NamedDict()
    param["job_id"] = "test_id"
    param["flow_id"] = "test_flow_id"
    param['TendrlContext.integration_id'] = "test_integration_id"
    param['TendrlContext.cluster_id'] = ""
    param["TendrlContext.cluster_name"] = ""
    param["Cluster.cluster_network"] = ""
    param["Cluster.public_network"] = ""
    param['create_mon_secret'] = True
    param["Cluster.node_configuration"] = {"test_node": maps.NamedDict(role="osd",provisioning_ip="test_ip",journal_colocation = "Test_var",journal_size = "test_size",storage_disks = [maps.NamedDict(device = "test_device")])}
    NS.ceph_provisioner = importlib.import_module("tendrl.commons.tests.fixtures.plugin").Plugin()
    NS.integrations = maps.NamedDict(ceph = maps.NamedDict())
    NS.integrations.ceph.objects = importlib.import_module("tendrl.commons.tests.fixtures.plugin").Plugin()
    with patch.object(Client,"read",return_value = maps.NamedDict(value = '{"test" :"json"}')):
        ceph_help.create_osds(param,["test_mon_ip"])
    param["Cluster.node_configuration"] = {"test_node": maps.NamedDict(role="osd",provisioning_ip="test_ip",journal_colocation = False,journal_size = "test_size",storage_disks = [maps.NamedDict(device = "test_device",journal = "test_jounal")])}
    with patch.object(Client,"read",return_value = maps.NamedDict(value = '{"test" :"json"}')):
        ceph_help.create_osds(param,["test_mon_ip"])


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('gevent.sleep',
            mock.Mock(return_value=True))
def test_wait_for_task():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    NS.ceph_provisioner = importlib.import_module("tendrl.commons.tests.fixtures.plugin").Plugin()
    with pytest.raises(FlowExecutionFailedError):
        ceph_help.wait_for_task("task_id_test")
    with pytest.raises(FlowExecutionFailedError):
        ceph_help.wait_for_task("task_test_id")
    with pytest.raises(FlowExecutionFailedError):
        ceph_help.wait_for_task("ret_none")
