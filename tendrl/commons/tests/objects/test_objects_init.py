import pytest
import maps
import __builtin__
from etcd import Client
import etcd
import pkgutil
import json
import mock
from tendrl.commons import objects
from tendrl.commons import TendrlNS
from mock import patch
import tendrl.commons.objects.node_context as node
from tendrl.commons.utils.central_store import utils as cs_utils


def hasattribute(*args):
    if args[0]:
        if args[1] == "internal":
            return True
        elif args[1] == "_defs":
            return False
        else:
            return True


def has_attr(*args):
    if args[0]:
        if args[1] == "internal":
            return True
        elif args[1] == "_defs":
            return True
        else:
            return True


def read(*args):
    raise etcd.EtcdConnectionFailed


def refresh(*args,**kwargs):
    raise etcd.EtcdConnectionFailed	

def hash(*args):
    raise TypeError

def refresh_client(*args,**kwargs):
    raise etcd.EtcdKeyNotFound	


@patch.object(etcd, "Client")
@patch.object(Client, "read")
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
    tendrlNS = TendrlNS()
    return tendrlNS


def obj_definition(*args,**kwargs):
    return maps.NamedDict()


def dumps(*args):
    raise ValueError


def write(*args,**kwargs):
    raise etcd.EtcdConnectionFailed


def test_constructor():
    with patch.object(__builtin__,'hasattr',hasattribute) as mock_hasattr:
        with pytest.raises(Exception):
            obj = objects.BaseObject()
            delattr(obj,"internal")
            mock_hasattr.return_value = hasattribute(False)
            obj.__init__()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_load_definition():
     tendrlNS = init()
     with patch.object(__builtin__,'hasattr',hasattribute) as mock_hasattr:
        with pytest.raises(Exception):
            obj = objects.BaseObject()
     with patch.object(__builtin__,'hasattr',has_attr) as mock_hasattr:    
        obj = objects.BaseObject()
        obj._ns = tendrlNS
        with pytest.raises(Exception):
            obj.load_definition()

@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.ExceptionMessage.__init__',
            mock.Mock(return_value=None))
def test_save():
    tendrlNS = init()
    with patch.object(__builtin__,'hasattr',has_attr) as mock_hasattr:    
        obj = objects.BaseObject()
        obj._ns = tendrlNS
        with patch.object(TendrlNS,'get_obj_definition',obj_definition) as mock_obj_definition:
            obj._defs = obj.load_definition()
            obj.value = 1
            obj.save()
            NS._int.wclient = etcd.Client()
            NS._int.wreconnect = type("Dummy",(object,),{})
            with patch.object(Client,"refresh",refresh) as mock_refresh:
                with pytest.raises(etcd.EtcdConnectionFailed):
                    obj.save(True,2)
            with patch.object(Client,"refresh",refresh_client) as mock_refresh_client:
                with patch.object(Client,"write",return_value = True) as mock_write:
                    obj.save(True,2)
            NS._int.client = etcd.Client()
            NS._int.reconnect = type("Dummy",(object,),{})
            with patch.object(Client,"read",read) as mock_read:
                with pytest.raises(etcd.EtcdConnectionFailed):
                    obj.save(True)
            hash_obj = obj._hash()
            with patch.object(Client,"write",return_value = None) as mock_write:
                with patch.object(Client,"read") as mock_read:
                    mock_read.return_value = maps.NamedDict(value = hash_obj)
                    obj.save(True)
            with patch.object(Client,"write",return_value = True) as mock_write:
                with patch.object(objects.BaseObject,"_hash",hash) as mock_hash:
                    obj.save(True)
            with patch.object(Client,"write",return_value = True) as mock_write:
                with patch.object(objects.BaseObject,"_hash",return_value = None) as mock_hash:
                    with patch.object(Client,"read") as mock_read:
                        mock_read.return_value = maps.NamedDict(value="")
                        with patch.object(objects.BaseObject,"load",return_value = maps.NamedDict(hash="")) as mock_load:
                            obj.save(True)
            with patch.object(Client,"write",return_value = True) as mock_write:
                with patch.object(Client,"read") as mock_read:
                    mock_read.return_value = maps.NamedDict(value="")
                    obj._defs = maps.NamedDict(attrs=maps.NamedDict(hash=maps.NamedDict(type="json")))
                    obj.save(False)
            with patch.object(Client,"write",write) as mock_write:
                with patch.object(Client,"read",return_value = maps.NamedDict(value="")) as mock_read:
                    with patch.object(objects.BaseObject,"_hash",return_value = "hash") as mock_hash:
                        with patch.object(json,"dumps",dumps) as mock_dumps:
                            with pytest.raises(etcd.EtcdConnectionFailed):
                                obj._defs = maps.NamedDict(attrs=maps.NamedDict(hash=maps.NamedDict(type="json")))
                                obj.__name__ = "Test"
                                NS.publisher_id = "node_context"
                                obj.save(False)
            with patch.object(Client,"write",return_value = True) as mock_write:
                obj.__class__.__name__ = "Message"
                obj.save()


def test_load():
    tendrlNS = init()
    with patch.object(__builtin__,'hasattr',has_attr) as mock_hasattr:    
        obj = objects.BaseObject()
        obj._ns = tendrlNS
        with patch.object(TendrlNS,'get_obj_definition',obj_definition) as mock_obj_definition:
            obj._defs = obj.load_definition()
            obj.value = 'Test'
            with patch.object(Client,"write",return_value = True) as mock_write:
                with patch.object(Client,"read",return_value = maps.NamedDict(value="Test")) as mock_read:
                    with patch.object(objects.BaseObject,'render',return_value = [{'value': '9fb712695c0f42dbf2edf13e6c03a828', 'dir': False, 'name': 'hash', 'key': '/1/hash'}]) as mock_render:
                        obj._defs = maps.NamedDict(attrs=maps.NamedDict(hash=maps.NamedDict(type="json")))
                        with pytest.raises(TypeError):
                            obj.load()
                with patch.object(Client,"read",read) as mock_read:
                    with patch.object(objects.BaseObject,'render',return_value = [{'value': '9fb712695c0f42dbf2edf13e6c03a828', 'dir': False, 'name': 'hash', 'key': '/1/hash'}]) as mock_render:
                        obj._defs = maps.NamedDict(attrs=maps.NamedDict(hash=maps.NamedDict(type="json")))
                        with pytest.raises(TypeError):
                            obj.load()
                with patch.object(Client,"read",return_value = True) as mock_read:
                    with patch.object(objects.BaseObject,'render',return_value = [{'value': '9fb712695c0f42dbf2edf13e6c03a828', 'dir': True, 'name': 'test', 'key': '/1/hash'}]) as mock_render:
                        with pytest.raises(AttributeError):
                            obj._defs = maps.NamedDict(attrs=maps.NamedDict(hash=maps.NamedDict(type="json")))
                            obj.test = {"Test":"test_variable"}
                            obj.load()

def test_exists():
    tendrlNS = init()
    with patch.object(__builtin__,'hasattr',has_attr) as mock_hasattr:    
        obj = objects.BaseObject()
        obj._ns = tendrlNS
        with patch.object(TendrlNS,'get_obj_definition',obj_definition) as mock_obj_definition:
            obj._defs = obj.load_definition()
            obj.value = 'Test'
            with patch.object(Client,"write",return_value = True) as mock_write:
                with patch.object(Client,"read",return_value = maps.NamedDict(value="Test")) as mock_read:
                    obj.exists()
                NS._int.client = etcd.Client()
                NS._int.reconnect = type("Dummy",(object,),{})
                with patch.object(Client,"read",read) as mock_read:
                    with pytest.raises(etcd.EtcdConnectionFailed):
                        obj.exists()
