import __builtin__
import etcd
from etcd import Client
import maps
from mock import patch
import pytest


from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects.node.atoms.is_node_tendrl_managed import \
    IsNodeTendrlManaged
from tendrl.commons.utils import etcd_utils


def read(*args, **kwargs):
    if args:
        if args[0] == "nodes/Test_node/Os":
            raise etcd.EtcdKeyNotFound
    else:
        return None


def test_constructor():
    IsNodeTendrlManaged()


@patch.object(etcd, "Client")
@patch.object(Client, "read")
@patch.object(etcd_utils, "read")
def test_run(mock_etcd_read, mock_read, mock_client):
    mock_read.return_value = read()
    mock_client.return_value = etcd.Client()
    obj = IsNodeTendrlManaged()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters["Node[]"] = []
    with pytest.raises(AtomExecutionFailedError):
        obj.run()
    obj.parameters["Node[]"] = ["Test_node"]
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    with patch.object(etcd.Client, 'read', read):
        obj.run()
    with patch.object(etcd.Client, 'read', read):
        obj.run()
    with patch.object(Client, "read", read):
        obj.run()
    mock_etcd_read.return_value = maps.NamedDict(
        leaves=None,
        value='{"status": "UP",'
              '"pkey": "tendrl-node-test",'
              '"node_id": "test_node_id",'
              '"ipv4_addr": "test_ip",'
              '"tags": "[\\"my_tag\\"]",'
              '"sync_status": "done",'
              '"locked_by": "fd",'
              '"fqdn": "tendrl-node-test",'
              '"leaves: None",'
              '"last_sync": "date"}')
    with pytest.raises(AtomExecutionFailedError):
        with patch.object(etcd_utils, "read", read):
            obj.run()
