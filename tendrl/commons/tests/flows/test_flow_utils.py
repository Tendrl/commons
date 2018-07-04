import __builtin__
import etcd
import importlib
import maps
import pytest

from mock import patch
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows import utils
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils.ssh import authorize_key


def mock_runner(*args, **attributes):
    return MockRunnerOb()


class MockRunnerOb(object):
    def run(self):
        raise ansible_module_runner.AnsibleExecutableGenerationFailed


class MockKey(object):
    def run(self):
        return "test_error", "test_error"


def test_install_gdeploy():
    NS.publisher_id = "node_context"
    with pytest.raises(FlowExecutionFailedError):
        utils.install_gdeploy()


def test_install_gdeploy_exception():
    with patch.object(ansible_module_runner, 'AnsibleRunner',
                      side_effect=ansible_module_runner.AnsibleModuleNotFound):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            utils.install_gdeploy()


def test_intall_gdeploy_exception2():
    with patch.object(ansible_module_runner.AnsibleRunner, 'run',
                      side_effect=ansible_module_runner.AnsibleExecutableGenerationFailed):  # noqa
        with pytest.raises(FlowExecutionFailedError):
            utils.install_gdeploy()


def test_install_pyton_gdeploy_pip():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS["node_context"] = maps.NamedDict()
    NS.node_context["node_id"] = "Test_node_id"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['package_source_type'] = 'pip'
    NS.publisher_id = "node_context"
    utils.install_python_gdeploy()


def test_install_pyton_gdeploy_rpm():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS["node_context"] = maps.NamedDict()
    NS.node_context["node_id"] = "Test_node_id"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['package_source_type'] = 'rpm'
    NS.publisher_id = "node_context"
    with pytest.raises(FlowExecutionFailedError):
        utils.install_python_gdeploy()


def test_install_python_gdeploy_fail():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS["node_context"] = maps.NamedDict()
    NS.node_context["node_id"] = "Test_node_id"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.publisher_id = "node_context"
    NS.config.data['package_source_type'] = 'test'
    with pytest.raises(FlowExecutionFailedError):
        utils.install_python_gdeploy()


def test_install_python_gdeploy_exception():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS["node_context"] = maps.NamedDict()
    NS.node_context["node_id"] = "Test_node_id"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['package_source_type'] = 'rpm'
    NS.publisher_id = "node_context"
    with patch.object(ansible_module_runner, 'AnsibleRunner',
                      side_effect = ansible_module_runner.AnsibleModuleNotFound):  # noqa
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            utils.install_python_gdeploy()


def test_install_pyton_gdeploy_gen_fail():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS["node_context"] = maps.NamedDict()
    NS.node_context["node_id"] = "Test_node_id"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['package_source_type'] = 'pip'
    NS.publisher_id = "node_context"
    with patch.object(ansible_module_runner, 'AnsibleRunner', mock_runner):
        with pytest.raises(FlowExecutionFailedError):
            utils.install_python_gdeploy()


# fail at sshkey generation
def test_gluster_create_ssh_setup_jobs_fails():
    testParams = maps.NamedDict()
    testParams['Node[]'] = []
    testParams["job_id"] = "test_id"
    testParams["flow_id"] = "test_id"

    with patch.object(etcd, "Client", return_value=etcd.Client()) as client:
        obj = importlib.import_module("tendrl.commons.tests.fixtures.client")
        NS._int.wclient = obj.Client()
        NS._int.client = client
        NS._int.watchers = dict()
        NS.tendrl = maps.NamedDict()
        NS.tendrl.objects = maps.NamedDict()
        NS.tendrl.objects.Job = Job(
            job_id=1,
            status="",
            payload=maps.NamedDict()
        ).save()
        NS.gluster_provisioner = importlib.import_module(
            "tendrl.commons.tests.fixtures.plugin").Plugin()
        with patch.object(NS.gluster_provisioner, 'setup',
                          return_value=["test_error", "test_error"]):
            with pytest.raises(FlowExecutionFailedError):
                utils.gluster_create_ssh_setup_jobs(testParams, True)


def test_gluster_create_ssh_setup_jobs_fails2():
    testParams = maps.NamedDict()
    testParams['Node[]'] = []
    testParams["job_id"] = "test_id"
    testParams["flow_id"] = "test_id"
    with patch.object(etcd, "Client", return_value=etcd.Client()) as client:
        obj = importlib.import_module("tendrl.commons.tests.fixtures.client")
        NS._int.wclient = obj.Client()
        NS._int.client = client
        NS._int.watchers = dict()
        NS.tendrl = maps.NamedDict()
        NS.tendrl.objects = maps.NamedDict()
        NS.tendrl.objects.Job = Job(
            job_id=1,
            status="",
            payload=maps.NamedDict()
        ).save()
        NS.gluster_provisioner = importlib.import_module(
            "tendrl.commons.tests.fixtures.plugin").Plugin()
        with patch.object(NS.gluster_provisioner, 'setup',
                          return_value=["", ""]):
            with patch.object(authorize_key, 'AuthorizeKey',
                              return_value=MockKey()):
                with pytest.raises(FlowExecutionFailedError):
                    utils.gluster_create_ssh_setup_jobs(
                        testParams, skip_current_node=False)


def test_gluster_create_ssh_setup_jobs_succeeds():
    testParams = maps.NamedDict()
    testParams['Node[]'] = ["Test Node", "Other Node"]
    testParams["job_id"] = "test_id"
    testParams["flow_id"] = "test_id"
    with patch.object(etcd, "Client", return_value=etcd.Client()) as client:
        obj = importlib.import_module("tendrl.commons.tests.fixtures.client")
        NS._int.wclient = obj.Client()
        NS._int.client = client
        NS._int.watchers = dict()
        NS.tendrl = maps.NamedDict()
        NS.tendrl.objects = maps.NamedDict()
        NS.tendrl.objects.Job = MockJob
        NS.node_context = maps.NamedDict()
        NS.node_context.node_id = "Test Node"
        NS.gluster_provisioner = importlib.import_module(
            "tendrl.commons.tests.fixtures.plugin").Plugin()
        with patch.object(NS.gluster_provisioner, 'setup',
                          return_value=["", ""]):
            utils.gluster_create_ssh_setup_jobs(testParams,
                                                skip_current_node=True)
        with patch.object(NS.gluster_provisioner, 'setup',
                          return_value=["", ""]):
            utils.gluster_create_ssh_setup_jobs(testParams,
                                                skip_current_node=False)


class MockNodeContextExists(object):

    def __init__(self, node_id=None, status=None):
        self.locked_by = "Test payload"

    def load(self):
        self.status = 'UP'
        return self

    def save(self):
        pass

    def exists(self):
        return True


class MockNodeContextNoKey(object):

    def __init__(self, node_id=None, status=None):
        self.locked_by = "Test payload"

    def load(self):
        self.status = 'UP'
        return self

    def save(self):
        raise etcd.EtcdKeyNotFound


class MockNodeContextExists2(object):

    def __init__(self, node_id=None, status=None):
        self.locked_by = "Not same payload"

    def load(self):
        self.status = 'UP'
        return self

    def exists(self):
        return True


class MockNodeContextDoesNotExist(object):

    def __init__(self, node_id=None, status=None):
        self.locked_by = None

    def exists(self):
        return False


class MockJob(object):

    def __init__(self, job_id=None, status=None, payload=None):
        self.locked_by = None
        self.payload = None

    def load(self):
        self.payload = {"parent": "Test payload"}
        return self

    def save(self):
        return self


class MockJobNoParent(object):

    def __init__(self, job_id=None, status=None, payload=None):
        self.locked_by = None
        self.payload = None

    def load(self):
        self.payload = {"not p": "Test payload"}
        return self


def test_acquire_node_lock():
    testParams = maps.NamedDict()
    testParams['Node[]'] = [0]
    testParams["job_id"] = "1"
    testParams["flow_id"] = "test_id"
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.NodeContext = MockNodeContextExists
    NS.tendrl.objects.Job = MockJob
    NS.publisher_id = 0
    utils.acquire_node_lock(testParams)
    NS.tendrl.objects.NodeContext = MockNodeContextExists2
    with pytest.raises(FlowExecutionFailedError):
        utils.acquire_node_lock(testParams)
    NS.tendrl.objects.NodeContext = MockNodeContextDoesNotExist
    with pytest.raises(FlowExecutionFailedError):
        utils.acquire_node_lock(testParams)
    NS.tendrl.objects.NodeContext = MockNodeContextExists
    NS.tendrl.objects.Job = MockJobNoParent
    utils.acquire_node_lock(testParams)


def test_release_node_lock():
    testParams = maps.NamedDict()
    testParams['Node[]'] = [0]
    testParams["job_id"] = "Test payload"
    testParams["flow_id"] = "test_id"
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.NodeContext = MockNodeContextExists
    NS.tendrl.objects.Job = MockJob
    NS.publisher_id = 0
    utils.release_node_lock(testParams)
    NS.tendrl.objects.NodeContext = MockNodeContextNoKey
    utils.release_node_lock(testParams)
