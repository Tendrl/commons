import __builtin__
import etcd
from etcd import Client
import json
import maps
import mock
from mock import patch
import pytest


from tendrl.commons import objects
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class BaseObject_Child(objects.BaseObject):
    def __init__(self, *args, **kwargs):
        if kwargs:
            self.test = kwargs["test"]
        self.value = "nodes/Test_object"
        self.updated_at = "latest"
        self._defs = maps.NamedDict(attrs=maps.NamedDict(
            value=maps.NamedDict(type="string"), updated_at=maps.NamedDict(
                type="string")))
        super(BaseObject_Child, self).__init__(*args, **kwargs)


class BaseAtom_Child(objects.BaseAtom):
    def __init__(self, parameter):
        self.__class__.__name__ = "write"
        super(BaseAtom_Child, self).__init__(parameter)

    def run(self):
        super(BaseAtom_Child, self).run()


''' Dummy Functions'''


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


def read(*args, **kwargs):
    raise etcd.EtcdConnectionFailed


def read_fn(*args, **kwargs):
    raise etcd.EtcdKeyNotFound


def refresh(*args, **kwargs):
    raise etcd.EtcdConnectionFailed


def hash(*args):
    raise TypeError


def refresh_client(*args, **kwargs):
    raise etcd.EtcdKeyNotFound


def obj_definition(*args, **kwargs):
    return maps.NamedDict()


def dumps(*args):
    raise ValueError


def write(*args, **kwargs):
    raise etcd.EtcdConnectionFailed


@patch.object(etcd, "Client")
@patch.object(Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
@patch.object(etcd_utils, 'read')
def init(patch_etcd_utils_read,
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
    tendrlNS = TendrlNS()
    return tendrlNS


def test_constructor():
    with patch.object(objects.BaseObject, 'load_definition',
                      return_value=maps.NamedDict()) as mock_load:
        BaseObject_Child()
        assert mock_load.called
    with patch.object(__builtin__, 'hasattr', return_value=True):
        BaseObject_Child()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.utils.log_utils.log',
            mock.Mock(return_value=None))
def test_load_definition():
    tendrlNS = init()
    with patch.object(__builtin__, 'hasattr', hasattribute):
        with pytest.raises(Exception):
            obj = BaseObject_Child()
    with patch.object(__builtin__, 'hasattr', has_attr):
        obj = BaseObject_Child()
        obj._ns = tendrlNS
        with pytest.raises(Exception):
            obj.load_definition()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.utils.log_utils.log',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.ExceptionMessage.__init__',
            mock.Mock(return_value=None))
def test_save():
    tendrlNS = init()
    with patch.object(__builtin__, 'hasattr', has_attr):
        obj = BaseObject_Child()
        obj._ns = tendrlNS
        with patch.object(TendrlNS, 'get_obj_definition', obj_definition):
            obj._defs = obj.load_definition()
            obj.value = "1"
            obj.save()
            NS._int.wclient = etcd.Client()
            with patch.object(Client, "refresh", refresh_client):
                with patch.object(Client, "write", return_value=True):
                    with pytest.raises(etcd.EtcdKeyNotFound):
                        obj.save(True, 2)
            NS._int.wreconnect = type("Dummy", (object,), {})
            with patch.object(Client, "refresh", refresh):
                with pytest.raises(etcd.EtcdConnectionFailed):
                    obj.save(True, 2)
            NS._int.client = etcd.Client()
            NS._int.reconnect = type("Dummy", (object,), {})
            with patch.object(Client, "read", read):
                with pytest.raises(etcd.EtcdConnectionFailed):
                    obj.save(True)
            hash_obj = obj._hash()
            with patch.object(Client, "write", return_value=None):
                with patch.object(Client, "read") as mock_read:
                    mock_read.return_value = maps.NamedDict(value=hash_obj)
                    obj.save(True)
            with patch.object(Client, "write", return_value=True):
                with patch.object(Client, "read",
                                  return_value=maps.NamedDict(value="")):
                        obj.save(True)
            with patch.object(Client, "write", return_value=True):
                with patch.object(objects.BaseObject, "_hash",
                                  return_value=None):
                    with patch.object(Client, "read") as mock_read:
                        mock_read.return_value = maps.NamedDict(value="")
                        with patch.object(objects.BaseObject, "load",
                                          return_value=maps.NamedDict(
                                              hash="")):
                            obj.save(True)
            with patch.object(Client, "write", return_value=True):
                with patch.object(Client, "read") as mock_read:
                    mock_read.return_value = maps.NamedDict(value="")
                    obj._defs = maps.NamedDict(attrs=maps.NamedDict(
                        hash=maps.NamedDict(type="json")))
                    obj.save(False)
            with patch.object(Client, "write", return_value=True):
                with patch.object(Client, "read") as mock_read:
                    mock_read.return_value = maps.NamedDict(value="")
                    obj._defs = maps.NamedDict(attrs=maps.NamedDict(
                        hash=maps.NamedDict(type="string")))
                    obj.save(False)
            with patch.object(Client, "write", write):
                with patch.object(Client, "read",
                                  return_value=maps.NamedDict(value="")):
                    with patch.object(objects.BaseObject, "_hash",
                                      return_value="hash"):
                        with pytest.raises(etcd.EtcdConnectionFailed):
                            obj._defs = maps.NamedDict(
                                attrs=maps.NamedDict(
                                    hash=maps.NamedDict(type="json")))
                            obj.__name__ = "Test"
                            NS.publisher_id = "node_context"
                            obj.save(False)

            with patch.object(Client, "write", return_value=True):
                with patch.object(Client, "read") as mock_read:
                    mock_read.return_value = maps.NamedDict(value="")
                    obj.__class__.__name__ = "Message"
                    with patch.object(objects.BaseObject, "render",
                                      return_value=[{'value': '',
                                                     'dir': False,
                                                     'name': 'hash',
                                                     'key': '/1/hash'}]):
                        obj.save(False)
            with patch.object(Client, "write", return_value=True):
                obj.__class__.__name__ = "Message"
                with patch.object(Client, "read",
                                  return_value=maps.NamedDict(value="")):
                    obj.save()


def test_load():
    tendrlNS = init()
    with patch.object(__builtin__, 'hasattr', has_attr):
        obj = BaseObject_Child()
        obj._ns = tendrlNS
        with patch.object(TendrlNS, 'get_obj_definition', obj_definition):
            obj._defs = obj.load_definition()
            obj.value = 'Test'
            with patch.object(Client, "write", return_value=True):
                with patch.object(Client, "read", return_value=maps.NamedDict(
                        value="Test")):
                    with patch.object(objects.BaseObject, 'render',
                                      return_value=[{'value': '9fb712695c0f42d'
                                                     'bf2edf13e6c03a828',
                                                     'dir': False,
                                                     'name': 'hash',
                                                     'key': '/1/hash'}]):
                        obj._defs = maps.NamedDict(attrs=maps.NamedDict(
                            hash=maps.NamedDict(type="json")))
                        with pytest.raises(TypeError):
                            obj.load()
                NS._int.client = etcd.Client()
                NS._int.reconnect = type("Dummy", (object,), {})
                with patch.object(Client, "read", read):
                    with patch.object(objects.BaseObject, 'render',
                                      return_value=[{'value':
                                                     '9fb712695c0f42dbf2ed'
                                                     'f13e6c03a828',
                                                     'dir': False,
                                                     'name': 'hash',
                                                     'key': '/1/hash'}]):
                        obj._defs = maps.NamedDict(attrs=maps.NamedDict(
                            hash=maps.NamedDict(type="json")))
                        with pytest.raises(etcd.EtcdConnectionFailed):
                            obj.load()
                        obj._defs = maps.NamedDict(attrs=maps.NamedDict(
                            hash=maps.NamedDict(type='')))
                        with pytest.raises(etcd.EtcdConnectionFailed):
                            obj.load()
                with patch.object(etcd_utils, "read",
                                  return_value=maps.NamedDict(
                                      {'value': '{"test_key": "test_value"}'})
                                  ):
                    with patch.object(objects.BaseObject, 'render',
                                      return_value=[{'value':
                                                     "9fb712695c0f42dbf2ed"
                                                     "f13e6c03a828",
                                                     'dir': False,
                                                     'name': 'hash',
                                                     'key': '/1/hash'}]):
                        obj._defs = maps.NamedDict(attrs=maps.NamedDict(
                            hash=maps.NamedDict(type='')))
                        obj.load()
                with patch.object(Client, "read",
                                  return_value=maps.NamedDict(
                                      {'value': '{"test_key": "test_value"}'})
                                  ):
                    with patch.object(objects.BaseObject, 'render',
                                      return_value=[{'value':
                                                     "9fb712695c0f42dbf2ed"
                                                     "f13e6c03a828",
                                                     'dir': False,
                                                     'name': 'hash',
                                                     'key': '/1/hash'}]):
                        obj._defs = maps.NamedDict(attrs=maps.NamedDict(
                            hash=maps.NamedDict(type='')))
                        obj.load()
                with patch.object(Client, "read", return_value=True):
                    with patch.object(objects.BaseObject, 'render',
                                      return_value=[{'value': 'test_val',
                                                     'dir': True, 'name':
                                                     'test',
                                                     'key': '/1/hash'}]):
                        with pytest.raises(AttributeError):
                            obj._defs = maps.NamedDict(attrs=maps.NamedDict(
                                hash=maps.NamedDict(type="json")))
                            obj.test = {"test": "test_variable"}
                            obj.load()
    with patch.object(objects.BaseObject, 'load_definition',
                      return_value=maps.NamedDict()):
        obj = BaseObject_Child()
        with patch.object(objects.BaseObject, 'render', return_value=[{
                'value': '9', 'dir': True, 'name': 'hash', 'key': '/1/hash'}]):
            with patch.object(Client, "read", return_value=maps.NamedDict(
                    value="Test")):
                with patch.object(Client, "read",
                                  return_value=maps.NamedDict(
                                      {'value': '{"test_key": "test_value"}'})
                                  ):
                    obj.load()
    with patch.object(objects.BaseObject, 'load_definition',
                      return_value=maps.NamedDict()):
        obj = BaseObject_Child()
        with patch.object(objects.BaseObject, 'render', return_value=[{
                'value': '9', 'dir': True, 'name': 'test', 'key': '/1/hash'}]):
            with patch.object(Client, "read",
                              return_value=maps.NamedDict(value="Test")):
                with patch.object(__builtin__, "hasattr", return_value=True):
                    with patch.object(Client, "read",
                                      return_value=maps.NamedDict(
                                          {'value':
                                               '{"test_key": "test_value"}'
                                           })
                                      ):
                        obj.test = "test_variable"
                        obj.load()
                        obj.test = {"test": "test_var"}
                        obj.load()


def test_exists():
    tendrlNS = init()
    with patch.object(__builtin__, 'hasattr', has_attr):
        obj = BaseObject_Child()
        obj._ns = tendrlNS
        with patch.object(TendrlNS, 'get_obj_definition', obj_definition):
            obj._defs = obj.load_definition()
            obj.value = 'Test'
            with patch.object(Client, "write", return_value=True):
                with patch.object(Client, "read",
                                  return_value=maps.NamedDict(value="Test")):
                    obj.exists()
                NS._int.client = etcd.Client()
                NS._int.reconnect = type("Dummy", (object,), {})
                with patch.object(Client, "read", read):
                    with pytest.raises(etcd.EtcdConnectionFailed):
                        obj.exists()


def test_load_all():
    tendrlNS = init()
    NS.publisher_id = "test"
    with patch.object(__builtin__, 'hasattr', has_attr):
        obj = BaseObject_Child()
        obj._ns = tendrlNS
        with patch.object(etcd_utils, "read", return_value=maps.NamedDict(
                leaves={})):
            obj.load_all()
        with patch.object(etcd_utils, "read", return_value=maps.NamedDict(
                leaves=[maps.NamedDict(key='test_value')])):
            with patch.object(BaseObject_Child, 'load', return_value="tst"):
                ret = obj.load_all()
                assert isinstance(ret, list)
        with patch.object(etcd_utils, "read", read):
            with pytest.raises(etcd.EtcdConnectionFailed):
                obj.load_all()
        with patch.object(etcd_utils, "read", read_fn):
            with patch.object(logger, "log"):
                ret = obj.load_all()
                assert ret == []


def test_constructor_BaseAtom():
    init()
    with patch.object(TendrlNS, 'get_atom_definition', return_value=True):
        BaseAtom_Child(1)
    with patch.object(__builtin__, 'hasattr', has_attr):
        BaseAtom_Child(1)
    with patch.object(__builtin__, 'hasattr', hasattribute):
        with pytest.raises(Exception):
            obj = BaseAtom_Child(1)
            assert obj.parameters == 1


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.utils.log_utils.log',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.ExceptionMessage.__init__',
            mock.Mock(return_value=None))
def test_load_definition_BaseAtom():
    tendrlNS = init()
    with patch.object(__builtin__, 'hasattr', has_attr):
        obj = BaseAtom_Child(1)
        obj._ns = tendrlNS
        with pytest.raises(Exception):
            obj._defs = obj.load_definition()


def test_run():
    with patch.object(__builtin__, 'hasattr', has_attr):
        obj = BaseAtom_Child(1)
        with pytest.raises(objects.AtomNotImplementedError):
            obj.run()


def test_constructor_AtomNotImplementedError():
    obj = objects.AtomNotImplementedError("Test Error")
    assert obj.message == "run function not implemented. Test Error"


def test_constructor_AtomExecutionFailedError():
    obj = objects.AtomExecutionFailedError("Test Error")
    assert obj.message == "Atom Execution failed. Error: Test Error"
