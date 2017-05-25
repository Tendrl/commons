import pytest
import maps
import __builtin__
from tendrl.commons.objects.node_context import NodeContext
from mock import patch
import mock
import etcd
import os


def read(*args):
    raise etcd.EtcdKeyNotFound
# Testing __init__
@patch.object(etcd, "Client")
@patch.object(NodeContext, '_get_node_id')
def test_constructor(patch_get_node_id, patch_client):
    '''
    Testing for constructor involves checking if all needed
    variales are declared initialized
    '''
    patch_get_node_id.return_value = 1
    patch_client.return_value = etcd.Client()
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    with patch.object(etcd.Client, "read",return_value = etcd.Client()) as mock_read:
        node_context = NodeContext()
        assert node_context is not None

@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
def test_get_node_id(patch_read, patch_client):
    patch_read.return_value = "8ceccbee-1e88-4232-9877-61d0ea595930"
    patch_client.return_value = etcd.Client()
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    with patch.object(os.path,"isfile",return_value=True) as mock_isfile:
        with mock.patch("__builtin__.open",create=True) as mock_open:
            mock_open.side_effect = [
			mock.mock_open(read_data="8ceccbee-1e88-4232-9877-61d0ea595930").return_value]
            with pytest.raises(Exception):
                node_context = NodeContext(machine_id = "8ceccbee-1e88-4232-9877-61d0ea595930")
    with patch.object(os.path,"isfile",return_value=False) as mock_isfile:
        with patch.object(NodeContext,"_create_node_id",return_value=None) as mock_create_node_id:
            node_context=NodeContext()

@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(etcd.Client, "write")
def test_get_machine_id(patch_write,patch_read, patch_client):
    patch_read.return_value = "8ceccbee-1e88-4232-9877-61d0ea595930"
    patch_write.return_value = etcd.Client()
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
    node_context=NodeContext(machine_id="Test_Machine_id", node_id="Test_Node_id", fqdn="Test_fqdn")
    def open(*args):
        raise IOError
    with patch.object(__builtin__,"open",open) as mock_open:
        ret = node_context._get_machine_id()

@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(etcd.Client, "write")
@patch.object(NodeContext, '_get_node_id')
def test_render(patch_get_node_id,patch_write,patch_read, patch_client):
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    patch_get_node_id.return_value = 1
    patch_client.return_value = etcd.Client()
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    with patch.object(etcd.Client, "read",return_value = etcd.Client()) as mock_read:
        node_context = NodeContext()
        node_context.render()


@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(etcd.Client, "write")
def test_create_node_id(patch_write,patch_read, patch_client):
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    patch_client.return_value = etcd.Client()
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
    node_context=NodeContext(machine_id="Test_Machine_id", node_id="Test_Node_id", fqdn="Test_fqdn")
    f = open('temp.txt','wb+')
    with patch.object(__builtin__,"open") as mock_open:
        mock_open.return_value = f
        with patch.object(os,"makedirs",return_value = True) as mock_makedirs:
            node_context._create_node_id()
    with pytest.raises(IOError):
        with patch.object(os,"makedirs",return_value = True) as mock_makedirs:
            node_context._create_node_id()
    f = open('temp.txt','wb+')
    with patch.object(__builtin__,"open") as mock_open:
        mock_open.return_value = f
        with patch.object(os.path,"exists",return_value = False) as mock_exists:
            with patch.object(os,"makedirs",return_value = True) as mock_makedirs:     
                node_context._create_node_id()

