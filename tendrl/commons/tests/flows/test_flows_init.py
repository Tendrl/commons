import builtins
import etcd
from etcd import Client
import importlib
import maps
import mock
from mock import patch
import pytest


from tendrl.commons import flows
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects.node.atoms.cmd import Cmd
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS
from tendrl.commons.utils import etcd_utils


''' Global Variables'''

internal_flag = 1
obj_flag = 1
obj = None
def_flag = 1


''' Child Classes'''


class BaseFlow_Child(flows.BaseFlow):

    def __init__(self, *args, **kwargs):
        self.__class__.__name__ = "ImportCluster"
        super(BaseFlow_Child, self).__init__(*args, **kwargs)

    def run(self):
        super(BaseFlow_Child, self).run()


''' Dummy Functions'''


def has_attr(*args):
    global internal_flag
    if args[1] == "internal" and internal_flag:
        internal_flag = internal_flag + 1
        return False
    else:
        return True
    if args[1] == "_defs":
        return True


def mock_hasattr(*args, **kwargs):
    global def_flag
    if args[1] == "_defs" and def_flag == 1:
        def_flag = 2
        return False
    return True


def set_defs(*args):
    if isinstance(args[0], BaseFlow_Child):
        args[0]._defs = maps.NamedDict(uuid="Test_uuid")
        global obj_flag
        if args[1] == "obj" and obj_flag < 3:
            obj_flag = obj_flag + 1
            return True
        elif args[1] == "obj":
            return False
    return True


def get_obj_definition(*args, **kwargs):
    def_obj = maps.NamedDict(
        {
            'attrs': {
                'integration_id': {
                    'type': 'String',
                    'help': 'Tendrl managed/generated cluster id for the sds '
                            'being managed by Tendrl'},
                'cluster_name': {
                    'type': 'String',
                    'help': 'Name of the cluster'},
                'node_id': {
                    'type': 'String',
                    'help': 'Tendrl ID for the managed node'},
                'cluster_id': {
                    'type': 'String',
                    'help': 'UUID of the cluster'},
                'sds_version': {
                    'type': 'String',
                    'help': "Version of the Tendrl managed sds, eg: '3.2.1'"},
                'sds_name': {
                    'type': 'String',
                    'help': "Name of the Tendrl managed sds, eg: 'gluster'"}},
            'help': 'Tendrl context',
            'obj_list': '',
            'enabled': True,
            'obj_value': 'nodes/$NodeContext.node_id/TendrlContext',
            'flows': {},
            'atoms': {}})
    def_obj.flows["ImportCluster"] = {
        'help': 'Tendrl context',
        'enabled': True,
        'type': 'test_type',
        'flows': {},
        'atoms': {},
        'inputs': 'test_input',
        'uuid': 'test_uuid'}
    return def_obj


def get_flow_definition(*args, **kwargs):
    return True


@patch.object(etcd, "Client")
@patch.object(Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
@patch.object(etcd_utils, 'read')
@patch.object(node.NodeContext, 'load')
def init(patch_node_load,
         patch_etcd_utils_read,
         patch_get_node_id,
         patch_read,
         patch_client):
    patch_get_node_id.return_value = 1
    patch_read.return_value = etcd.Client()
    patch_client.return_value = etcd.Client()
    setattr(builtins, "NS", maps.NamedDict())
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
    patch_node_load.return_value = node.NodeContext
    tendrlNS = TendrlNS()
    return tendrlNS


'''Unit Test Cases for Base Flow Class'''


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.utils.log_utils.log',
            mock.Mock(return_value=None))
def test_constructor():
    with patch.object(flows.BaseFlow, 'load_definition',
                      return_value=maps.NamedDict(uuid="Test_uuid")) as \
            mock_load:
        BaseFlow_Child()
        assert mock_load.called
        with patch.object(builtins, 'hasattr', has_attr) as mock_hasattr:
            BaseFlow_Child()
    with patch.object(builtins, 'hasattr', mock_hasattr):
        with pytest.raises(Exception):
            BaseFlow_Child()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.utils.log_utils.log',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.ExceptionMessage.__init__',
            mock.Mock(return_value=None))
def test_load_definition():
    tendrlNS = init()
    with patch.object(builtins, 'hasattr', set_defs):
        flow_obj = BaseFlow_Child()
        flow_obj._ns = tendrlNS
        flow_obj.obj = importlib.import_module(
            "tendrl.commons.objects.node").Node
        with pytest.raises(Exception):
            flow_obj.load_definition()
        with patch.object(TendrlNS, 'get_obj_definition', get_obj_definition):
            ret = flow_obj.load_definition()
            assert ret is not None
        with pytest.raises(Exception):
            flow_obj.load_definition()
        with patch.object(TendrlNS, 'get_flow_definition',
                          get_flow_definition):
            ret = flow_obj.load_definition()
            assert ret is not None


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.utils.log_utils.log',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.ExceptionMessage.__init__',
            mock.Mock(return_value=None))
def test_run():
    init()
    with patch.object(builtins, 'hasattr', set_defs):
        flow_obj = BaseFlow_Child()
        global obj
        flow_obj._defs = get_obj_definition()
        flow_obj.to_str = "ImportCluster"
        flow_obj.run()
        flow_obj._defs['inputs'] = maps.NamedDict(mandatory=[])
        with mock.patch('tendrl.commons.utils.log_utils.log',
                        mock.Mock(return_value=None)) as mock_msg:
            flow_obj.run()
            assert mock_msg.assert_called
        flow_obj._defs['inputs'] = maps.NamedDict(
            mandatory=['job_id', 'flow_id'])
        flow_obj.run()
        flow_obj._defs['pre_run'] = None
        flow_obj.run()
        flow_obj._defs['pre_run'] = ["tendrl.objects.node.atoms.cmd"]
        with pytest.raises(AtomExecutionFailedError):
            flow_obj.run()
        flow_obj._defs['pre_run'] = ["tendrl.objects.Node.atoms.Cmd"]
        with patch.object(Cmd, 'run', return_value=True):
            flow_obj.run()
        flow_obj._defs['pre_run'] = None
        flow_obj._defs['atoms'] = None
        flow_obj.run()
        flow_obj._defs['atoms'] = ["tendrl.objects.node.atoms.cmd"]
        with pytest.raises(AtomExecutionFailedError):
            flow_obj.run()
        flow_obj._defs['atoms'] = ["tendrl.objects.Node.atoms.Cmd"]
        with patch.object(Cmd, 'run', return_value=True):
            flow_obj.run()
        flow_obj._defs['atoms'] = None
        flow_obj._defs['post_run'] = None
        flow_obj.run()
        flow_obj._defs['post_run'] = ["tendrl.objects.node.atoms.cmd"]
        with pytest.raises(AtomExecutionFailedError):
            flow_obj.run()
        flow_obj._defs['post_run'] = ["tendrl.objects.Node.atoms.Cmd"]
        with patch.object(Cmd, 'run', return_value=True):
            flow_obj.run()
        flow_obj._defs['post_run'] = [
            "tendrl.integrations.objects.Node.atoms.Cmd"]
        with pytest.raises(AtomExecutionFailedError):
            flow_obj.run()
