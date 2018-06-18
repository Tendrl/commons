import __builtin__
import etcd
import importlib
import maps
from mock import patch
import pytest


from tendrl.commons.tests.fixtures.client import Client
from tendrl.commons.utils import etcd_utils


'''Dummy Functions'''


def raise_etcdconnectionfailed(*args, **kwargs):
    raise etcd.EtcdConnectionFailed


def raise_etcdkeynotfound(*args, **kwargs):
    raise etcd.EtcdKeyNotFound


def test_read():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.client = importlib.import_module("tendrl.commons"
                                             ".tests.fixtures."
                                             "client").Client()
    NS._int.reconnect = type("Dummy", (object,), {})
    with patch.object(Client, "read",
                      return_value="test") as mock_read:
        obj = etcd_utils.read("key")
        assert obj == "test"
        assert mock_read.assert_called
    with patch.object(Client, "read",
                      raise_etcdconnectionfailed) as mock_read:
        with pytest.raises(etcd.EtcdConnectionFailed):
            obj = etcd_utils.read("key")
    with patch.object(Client,
                      "read", raise_etcdkeynotfound) as mock_read:
        with pytest.raises(etcd.EtcdKeyNotFound):
            obj = etcd_utils.read("key")


def test_write():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.wclient = importlib.import_module("tendrl.commons"
                                              ".tests.fixtures."
                                              "client").Client()
    NS._int.wreconnect = type("Dummy", (object,), {})
    with patch.object(Client, "write") as mock_write:
        etcd_utils.write("key", "test_value", False)
        assert mock_write.assert_called
    with patch.object(Client, "write",
                      raise_etcdconnectionfailed) as mock_write:
        with pytest.raises(etcd.EtcdConnectionFailed):
            etcd_utils.write("key", "test_value", False)
    with patch.object(Client, "write",
                      raise_etcdkeynotfound) as mock_write:
        with pytest.raises(etcd.EtcdKeyNotFound):
            etcd_utils.write("key", "test_value", False)


def test_refresh():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.wclient = importlib.import_module("tendrl.commons"
                                              ".tests.fixtures."
                                              "client").Client()
    NS._int.wreconnect = type("Dummy", (object,), {})
    with patch.object(Client, "refresh") as mock_refresh:
        etcd_utils.refresh("test_value", 1)
        assert mock_refresh.assert_called
    with patch.object(Client, "refresh",
                      raise_etcdconnectionfailed) as mock_refresh:
        with pytest.raises(etcd.EtcdConnectionFailed):
            etcd_utils.refresh("test_value", 1)
    with patch.object(Client, "refresh",
                      raise_etcdkeynotfound) as mock_refresh:
        with pytest.raises(etcd.EtcdKeyNotFound):
            etcd_utils.refresh("test_value", 1)


def test_delete():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.wclient = importlib.import_module("tendrl.commons"
                                              ".tests.fixtures."
                                              "client").Client()
    NS._int.wreconnect = type("Dummy", (object,), {})
    with patch.object(Client, "delete") as mock_delete:
        etcd_utils.delete("key")
        assert mock_delete.assert_called
    with patch.object(Client, "delete",
                      raise_etcdconnectionfailed) as mock_delete:
        with pytest.raises(etcd.EtcdConnectionFailed):
            etcd_utils.delete("key")
    with patch.object(Client, "delete",
                      raise_etcdkeynotfound) as mock_delete:
        with pytest.raises(etcd.EtcdKeyNotFound):
            etcd_utils.delete("key")
