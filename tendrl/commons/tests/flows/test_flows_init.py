import pytest
import maps
import __builtin__
from etcd import Client
import etcd
import pkgutil
import json
import mock
from tendrl.commons import flows
from tendrl.commons import TendrlNS
from mock import patch
import importlib
import tendrl.commons.objects.node_context as node
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects.node.atoms.cmd import Cmd


import sys

''' Global Variables'''
internal_flag = 1
obj_flag = 1
obj = None

''' Child Classes'''

class TestBaseFlow(flows.BaseFlow):

    def __init__(self,*args,**kwargs):
        self.__class__.__name__ = "ImportCluster"
        super(TestBaseFlow,self).__init__(*args,**kwargs)

    def run(self):
        super(TestBaseFlow,self).run()

''' Dummy Functions'''

def has_attr(*args):
    global internal_flag
    if args[1] == "internal" and internal_flag:
        internal_flag = internal_flag+1
        return False
    else:
        return True 
    if args[1] == "_defs":
        return True

def mock_hasattr(*args,**kwargs):
    if args[1] == "_defs":
        return False
    return True

def set_defs(*args):
    if isinstance(args[0],TestBaseFlow):
        args[0]._defs = maps.NamedDict(uuid = "Test_uuid")
        global obj_flag
        if args[1] == "obj" and obj_flag < 3:
            obj_flag = obj_flag + 1
            return True
        elif args[1] == "obj":
            return False
    return True    

def get_obj_definition(*args,**kwargs):
    ret = maps.NamedDict({'attrs': {'integration_id': {'type': 'String', 'help': 'Tendrl managed/generated cluster id for the sds being managed by Tendrl'}, 'cluster_name': {'type': 'String', 'help': 'Name of the cluster'}, 'node_id': {'type': 'String', 'help': 'Tendrl ID for the managed node'}, 'cluster_id': {'type': 'String', 'help': 'UUID of the cluster'}, 'sds_version': {'type': 'String', 'help': "Version of the Tendrl managed sds, eg: '3.2.1'"}, 'sds_name': {'type': 'String', 'help': "Name of the Tendrl managed sds, eg: 'gluster'"}}, 'help': 'Tendrl context', 'obj_list': '', 'enabled': True, 'obj_value': 'nodes/$NodeContext.node_id/TendrlContext', 'flows': {}, 'atoms': {}})
    ret.flows["ImportCluster"] = {'help': 'Tendrl context', 'enabled': True, 'type': 'test_type', 'flows': {}, 'atoms': {},'inputs':'test_input','uuid':'test_uuid'}
    return ret

def get_flow_definition(*args,**kwargs):
    return True

    
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
    NS.publisher_id = "node_context"
    tendrlNS = TendrlNS()
    return tendrlNS

'''Unit Test Cases for Base Flow Class'''


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_constructor():
    with patch.object(flows.BaseFlow,'load_definition',return_value = maps.NamedDict(uuid = "Test_uuid")) as mock_load:
        flow_obj = TestBaseFlow()
        assert mock_load.called
        with patch.object(__builtin__,'hasattr',has_attr) as mock_hasattr:
            flow_obj = TestBaseFlow()
    with patch.object(__builtin__,'hasattr',mock_hasattr) as mock_fn:
        with pytest.raises(Exception):
            flow_obj = TestBaseFlow()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.ExceptionMessage.__init__',
            mock.Mock(return_value=None))
def test_load_definition():
     tendrlNS = init()
     with patch.object(__builtin__,'hasattr',set_defs) as mock_hasattr:
        flow_obj = TestBaseFlow()
        flow_obj._ns = tendrlNS
        flow_obj.obj = importlib.import_module("tendrl.commons.objects.node").Node
        with pytest.raises(Exception):
            flow_obj.load_definition()
        with patch.object(TendrlNS,'get_obj_definition',get_obj_definition) as mock_fn:
            ret = flow_obj.load_definition()
            assert ret is not None
            #assert mock_fn.called
        with pytest.raises(Exception):
            flow_obj.load_definition()
        with patch.object(TendrlNS,'get_flow_definition',get_flow_definition) as mock_fn:
            flow_obj.load_definition()
            #assert mock_fn.called


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.ExceptionMessage.__init__',
            mock.Mock(return_value=None))
def test_run():
    tendrlNS = init()
    with patch.object(__builtin__,'hasattr',set_defs) as mock_hasattr:
        flow_obj = TestBaseFlow()
        global obj
        flow_obj._defs = get_obj_definition()
        flow_obj.to_str = "ImportCluster"
        flow_obj.run()
        flow_obj._defs['inputs'] = maps.NamedDict(mandatory = [''])
        flow_obj.run()
        flow_obj._defs['inputs'] = maps.NamedDict(mandatory = ['job_id','flow_id'])
        flow_obj.run()
        flow_obj._defs['pre_run'] = None
        flow_obj.run()
        flow_obj._defs['pre_run'] = ["tendrl.commons.objects.node.atoms.cmd"]
        NS["commons"] = NS.tendrl
        with pytest.raises(AtomExecutionFailedError):
            flow_obj.run()
        flow_obj._defs['pre_run'] = ["tendrl.commons.objects.Node.atoms.Cmd"]
        with patch.object(Cmd,'run',return_value = True) as mock_run:
            flow_obj.run()
        flow_obj._defs['pre_run'] = None
        flow_obj._defs['atoms'] = None
        flow_obj.run()
        flow_obj._defs['atoms'] = ["tendrl.commons.objects.node.atoms.cmd"]
        with pytest.raises(AtomExecutionFailedError):
            flow_obj.run()
        flow_obj._defs['atoms'] = ["tendrl.commons.objects.Node.atoms.Cmd"]
        with patch.object(Cmd,'run',return_value = True) as mock_run:
            flow_obj.run()
        flow_obj._defs['atoms'] = None
        flow_obj._defs['post_run'] = None
        flow_obj.run()
        flow_obj._defs['post_run'] = ["tendrl.commons.objects.node.atoms.cmd"]
        with pytest.raises(AtomExecutionFailedError):
            flow_obj.run()
        flow_obj._defs['post_run'] = ["tendrl.commons.objects.Node.atoms.Cmd"]
        with patch.object(Cmd,'run',return_value = True) as mock_run:
            flow_obj.run()
        flow_obj._defs['post_run'] = ["tendrl.commons.integrations.objects.Node.atoms.Cmd"]
        with pytest.raises(AtomExecutionFailedError):
            flow_obj.run()
