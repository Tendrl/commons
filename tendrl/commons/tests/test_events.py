import __builtin__
import etcd
from etcd import Client
import maps
from mock import MagicMock
from mock import patch

from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.objects import BaseObject
import tendrl.commons.objects.node_context as node
import tendrl.commons.objects.tendrl_context as tendrl_context
from tendrl.commons import TendrlNS
from tendrl.commons.utils import etcd_utils


# init that does not have the built in attribute
# Code was not being covered when only in the test_init file
# Some problem with the events test in this file was causing the
# problem. So put this before that test so that it would be covered
@patch.object(tendrl_context.TendrlContext, "load")
@patch.object(etcd, "Client")
@patch.object(Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
@patch.object(etcd_utils, 'read')
def init(patch_etcd_utils_read,
         patch_get_node_id,
         patch_read,
         patch_client,
         tc):
    tc.return_value = tendrl_context.TendrlContext
    patch_get_node_id.return_value = 1
    patch_read.return_value = etcd.Client()
    patch_client.return_value = etcd.Client()
    # setattr(__builtin__, "NS", maps.NamedDict())
    # setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    patch_etcd_utils_read.return_value = maps.NamedDict(
        value='{"status": "UP",'
              '"pkey": "tendrl-node-test",'
              '"node_id": "test_node_id",'
              '"ipv4_addr": "test_ip",'
              '"tags": "[\\"my_tag\\"]",'
              '"sync_status": "done",'
              '"locked_by": "fd",'
              '"fqdn": "",'
              '"last_sync": "date"}')
    with patch.object(etcd_utils, "read") as utils_read:
        utils_read.return_value = maps.NamedDict(
            value='{"tags":[]}'
        )
        with patch.object(BaseObject, "load") as node_load:
            node.load = MagicMock()
            node_load.return_value = node
    tendrlNS = TendrlNS()
    return tendrlNS


def test_constructor():
    with patch.object(TendrlNS, 'setup_common_objects') as \
            mocked_method:
        mocked_method.return_value = None
        tendrlNS = TendrlNS()
    tendrlNS = init()
    # Default Parameter Testing
    assert tendrlNS.ns_name == "tendrl"
    assert tendrlNS.ns_src == "tendrl.commons"
    # Check for existance and right data type
    assert isinstance(NS, maps.NamedDict)


# Event Dummys provide code coverage for the Event constructor
message_new = msg = Message(priority="info", publisher="node_agent",
                            payload={"message": "Test Message"},
                            node_id="Test id")
event_dummy = Event(Message(priority="info", publisher="node_agent", payload={
    "message": "Test Message"}, node_id="Test id"))
event_dummy2 = Event(Message(priority="info", publisher="node_agent", payload={
    "message": TypeError}, node_id="Test id"))


def test_write():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    NS.publisher_id = "node_context"
    NS.config.data['logging_socket_path'] = "/var/run/tendrl/message.sock"
    event_to_test = Event(Message(priority="info", publisher="node", payload={
        "message": "Test message"}, node_id="Test id"))
    event_to_test._write(message_new)
    event_to_test.socket_path = None
    event_to_test._write(message_new)
