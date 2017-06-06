import __builtin__
from tendrl.commons.flows.import_cluster import gluster_help
from tendrl.commons.utils import ansible_module_runner
import maps
import mock
from mock import patch
import pytest


def run(*args):
    raise ansible_module_runner.AnsibleExecutableGenerationFailed


def ansible(*args,**kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_import_gluster():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    NS.config.data['package_source_type'] = 'test pip'
    parameters = maps.NamedDict(job_id = 1,flow_id= 1)
    assert gluster_help.import_gluster(parameters) is False
    NS.config.data['package_source_type'] = 'pip'
    with patch.object(ansible_module_runner.AnsibleRunner,'run',run) as mock_run:
        ret = gluster_help.import_gluster(parameters)
        assert ret is False
    with patch.object(ansible_module_runner.AnsibleRunner,'run',return_value = True) as mock_run:
        ret = gluster_help.import_gluster(parameters)
    with patch.object(ansible_module_runner,'AnsibleRunner',ansible) as mock_ansible:
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            ret = gluster_help.import_gluster(parameters)
    NS.config.data['package_source_type'] = 'rpm'
    with patch.object(ansible_module_runner.AnsibleRunner,'run',run) as mock_run:
        ret = gluster_help.import_gluster(parameters)
        assert ret is False
    
