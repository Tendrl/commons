import builtins
import etcd
import maps
import mock
from mock import patch
import tempfile


from tendrl.commons.flows.import_cluster import gluster_help
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS
from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils.service_status import ServiceStatus


'''Dummy Functions'''


def run(*args):
    raise ansible_module_runner.AnsibleExecutableGenerationFailed


def ansible(*args, **kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


def open(*args, **kwargs):
    f = tempfile.TemporaryFile()
    return f


'''Unit Test Cases'''


@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
@patch.object(etcd_utils, 'read')
def init(patch_etcd_utils_read,
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
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    NS.node_context['fqdn'] = "test_fqdn"
    NS.config.data['package_source_type'] = 'test pip'
    NS.config.data['tags'] = "test"
    NS.config.data['etcd_port'] = 8085
    NS.config.data['etcd_connection'] = "Test Connection"
    NS.config.data['sync_interval'] = 30
    NS.compiled_definitions = mock.MagicMock()
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


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('os.chmod',
            mock.Mock(return_value=None))
def test_import_gluster():
    tendrlNS = init()
    # import pdb; pdb.set_trace();
    NS.compiled_definitions = tendrlNS.current_ns.definitions
    parameters = maps.NamedDict(job_id=1, flow_id=1)
    ret_val, err = gluster_help.import_gluster(parameters)
    assert ret_val is False
    assert err is not None
    NS.config.data['package_source_type'] = 'pip'
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        ret, err = gluster_help.import_gluster(parameters)
        assert ret is False
    with patch.object(ansible_module_runner.AnsibleRunner, 'run',
                      return_value=({"rc": 1, "msg": None}, None)):
        ret, err = gluster_help.import_gluster(parameters)
        assert ret is False
    NS.config.data['package_source_type'] = 'rpm'
    with patch.object(ansible_module_runner.AnsibleRunner, 'run',
                      return_value=({"rc": 0, "msg": None}, None)):
        with patch.object(builtins, 'open', open):
            with patch.object(cmd_utils.Command, 'run',
                              return_value=("err", "", 1)):
                ret, err = gluster_help.import_gluster(parameters)
        assert ret is False
    with patch.object(ansible_module_runner.AnsibleRunner, 'run',
                      return_value=({"rc": 0, "msg": None}, None)):
        with patch.object(builtins, 'open', open):
            with patch.object(cmd_utils.Command, 'run',
                              return_value=(None, "", 0)):
                with patch.object(ServiceStatus, 'status',
                                  return_value=True):
                    ret, err = gluster_help.import_gluster(parameters)
        assert ret is True
