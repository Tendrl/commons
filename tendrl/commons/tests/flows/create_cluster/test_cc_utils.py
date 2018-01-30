import __builtin__
import importlib
import maps
import mock
from mock import patch
import pytest
import uuid


from tendrl.commons.flows.create_cluster import utils
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.tests.fixtures.plugin import Plugin
from tendrl.commons.utils import ansible_module_runner

'''Dummy Functions'''


def run(*args):
    raise ansible_module_runner.AnsibleExecutableGenerationFailed


def ansible(*args, **kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


'''Unit Test Functions'''


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.save',
            mock.Mock(return_value=None))
@mock.patch('time.sleep',
            mock.Mock(return_value=True))
def test_ceph_create_ssh_setup_jobs():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    param = maps.NamedDict()
    param['Node[]'] = []
    param["Cluster.node_configuration"] = {
        "test_node": maps.NamedDict(role="osd", provisioning_ip="test_ip")}
    NS.ceph_provisioner = importlib.import_module(
        "tendrl.commons.tests.fixtures.plugin").Plugin()
    ret = utils.ceph_create_ssh_setup_jobs(param)
    assert ret == []
    param['Node[]'] = ['test_node']
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = "test_node"
    ret = utils.ceph_create_ssh_setup_jobs(param)
    assert ret == []
    NS.node_context.node_id = "node"
    param["job_id"] = "test_id"
    param["flow_id"] = "test_flow_id"
    ret = utils.ceph_create_ssh_setup_jobs(param)
    str(uuid.uuid4())
    assert ret is not None


@mock.patch('time.sleep',
            mock.Mock(return_value=True))
def test_install_gdeploy():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    with patch.object(ansible_module_runner, 'AnsibleRunner', ansible):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            utils.install_gdeploy()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        with pytest.raises(FlowExecutionFailedError):
            utils.install_gdeploy()


@mock.patch('time.sleep',
            mock.Mock(return_value=True))
def test_install_python_gdeploy():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    NS.config.data['package_source_type'] = "pip"
    utils.install_python_gdeploy()
    with patch.object(ansible_module_runner, 'AnsibleRunner', ansible):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            utils.install_python_gdeploy()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        with pytest.raises(FlowExecutionFailedError):
            utils.install_python_gdeploy()
    NS.config.data['package_source_type'] = "test"
    with pytest.raises(FlowExecutionFailedError):
        utils.install_python_gdeploy()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.save',
            mock.Mock(return_value=None))
@mock.patch('time.sleep',
            mock.Mock(return_value=True))
def test_gluster_create_ssh_setup_jobs():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_context"
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    param = maps.NamedDict()
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    param["job_id"] = "test_id"
    param["flow_id"] = "test_flow_id"
    param['Node[]'] = ['test_node']
    NS.gluster_provisioner = importlib.import_module(
        "tendrl.commons.tests.fixtures.plugin").Plugin()
    param['TendrlContext.integration_id'] = "test_integration_id"
    with pytest.raises(FlowExecutionFailedError):
        utils.gluster_create_ssh_setup_jobs(param, True)
    with patch.object(Plugin, 'setup') as mock_setup:
        mock_setup.return_value = "ssh_key", ""
        ret = utils.gluster_create_ssh_setup_jobs(param, True)
        assert isinstance(ret, list)
    NS.node_context.node_id = 'test_node'
    with patch.object(Plugin, 'setup') as mock_setup:
        mock_setup.return_value = "ssh_key", ""
        ret = utils.gluster_create_ssh_setup_jobs(param, True)
        assert ret == []
    with patch.object(Plugin, 'setup') as mock_setup:
        with pytest.raises(FlowExecutionFailedError):
            mock_setup.return_value = "ssh_key", ""
            utils.gluster_create_ssh_setup_jobs(param)
