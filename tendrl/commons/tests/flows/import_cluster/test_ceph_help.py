import __builtin__
import etcd
import maps
import mock
from mock import patch
import pytest
from ruamel import yaml
import tempfile

from tendrl.commons.flows.import_cluster import ceph_help
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS
from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils import cmd_utils

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
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    NS.config.data['package_source_type'] = 'test pip'
    NS.config.data['tags'] = "test"
    NS.config.data['etcd_port'] = 8085
    NS.config.data['etcd_connection'] = "Test Connection"
    NS.config.data['sync_interval'] = 30
    NS.compiled_definitions = mock.MagicMock()
    tendrlNS = TendrlNS()
    return tendrlNS


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@patch.object(yaml, "dump")
def test_import_ceph(dump):
    dump.return_value = None
    tendrlNS = init()
    parameters = maps.NamedDict(job_id=1, flow_id=1)
    assert ceph_help.import_ceph(parameters) is False
    NS.config.data['package_source_type'] = 'pip'
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        ret = ceph_help.import_ceph(parameters)
        assert ret is False
    NS.config.data['package_source_type'] = 'rpm'
    with patch.object(ansible_module_runner.AnsibleRunner, 'run',
                      return_value=({"rc" : 0, "msg": None}, None)):
        with patch.object(__builtin__,'open',open) as mock_open:
            ret = ceph_help.import_ceph(parameters)
