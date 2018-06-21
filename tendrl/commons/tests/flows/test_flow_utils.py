
import __builtin__

from tendrl.commons.utils import ansible_module_runner
import etcd
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
import importlib
from tendrl.commons.objects.job import Job
from tendrl.commons.flows import utils
import maps
from mock import patch

import pytest

def test_install_gdeploy():
    NS.publisher_id = "node_context"
    with pytest.raises(FlowExecutionFailedError):
        utils.install_gdeploy()

def test_install_gdeploy_exception():
    with patch.object(ansible_module_runner, 'AnsibleRunner',
                      side_effect=ansible_module_runner.AnsibleModuleNotFound) as foo:
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            utils.install_gdeploy()

def test_intall_gdeploy_exception2():
    with patch.object(ansible_module_runner.AnsibleRunner, 'run',
                      side_effect=ansible_module_runner.AnsibleExecutableGenerationFailed) as foo:
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
    with pytest.raises(FlowExecutionFailedError):
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
                      side_effect=ansible_module_runner.AnsibleModuleNotFound) as foo:
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
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
            job_id= 1,
            status="",
            payload= maps.NamedDict()
        ).save()
        NS.gluster_provisioner = importlib.import_module(
            "tendrl.commons.tests.fixtures.plugin").Plugin()
        with patch.object(NS.gluster_provisioner, 'setup',
                          return_value=["test_error","test_error"]) as foo:
            with pytest.raises(FlowExecutionFailedError):
                utils.gluster_create_ssh_setup_jobs(testParams, True)

# fail at skip_current_node = false
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
            job_id= 1,
            status="",
            payload= maps.NamedDict()
        ).save()
        NS.gluster_provisioner = importlib.import_module(
            "tendrl.commons.tests.fixtures.plugin").Plugin()
        with patch.object(NS.gluster_provisioner, 'setup',
                          return_value=["",""]) as foo:
            utils.gluster_create_ssh_setup_jobs(testParams, skip_current_node=True)

def test_acquire_node_lock():
    testParams = maps.NamedDict()
    testParams['Node[]'] = [0]
    testParams["job_id"] = ""
    testParams["flow_id"] = "test_id"
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()

    utils.acquire_node_lock(testParams)