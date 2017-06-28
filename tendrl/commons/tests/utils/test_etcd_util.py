import pytest
from tendrl.commons.utils import etcd_utils
import __builtin__
import maps
import importlib
from mock import patch
from tendrl.commons.tests.fixtures.client import Client
import etcd


'''Dummy Functions'''


def raise_etcdconnectionfailed(*args, **kwargs):
    raise etcd.EtcdConnectionFailed


def raise_etcdkeynotfound(*args, **kwargs):
    raise etcd.EtcdKeyNotFound


'''Unit Test Cases'''


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

