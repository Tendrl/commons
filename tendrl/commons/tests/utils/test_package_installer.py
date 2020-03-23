import builtins
import maps
import mock
from mock import patch
import os
import pytest


from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils.package_installer import Installer


def ansible_run(*args):
    if args[0]:
        return {"msg": "test_msg", "rc": 0}, "Error"
    else:
        return {"msg": "test_msg", "rc": 1}, "Error"


def ansible(*args, **kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


def run(*args):
    raise ansible_module_runner.AnsibleExecutableGenerationFailed


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_constructor():
    setattr(builtins, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    obj_installer = Installer("mock", "pip", "1.1")
    assert isinstance(obj_installer.attributes, dict)
    assert obj_installer.attributes["name"] == "mock-1.1"
    obj_installer = Installer("test_rpm", "rpm", "1.1")
    assert obj_installer.ansible_module_path == "packaging/os/yum.py"
    obj_installer = Installer("test_deb", "deb", "1.1")
    assert obj_installer.ansible_module_path == "packaging/os/apt.py"
    with pytest.raises(ValueError):
        Installer("test_deb", "test_deb", "1.1")
    Installer("test_deb", "deb")


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_install():
    setattr(builtins, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    obj_installer = Installer("mock", "pip", "1.1")
    with patch.object(ansible_module_runner, 'AnsibleRunner', ansible):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            obj_installer.install()
            assert obj_installer.ansible_module_path == \
                "core/packaging/language/pip.py"
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            ret = obj_installer.install()
            assert ret[1] is False
    with patch.object(os.path, 'isfile', return_value=True):
        with patch.object(ansible_module_runner.AnsibleRunner, 'run') as \
                mock_run:
            mock_run.return_value = ansible_run(True)
            ret = obj_installer.install()
            assert ret[1] is True
            mock_run.return_value = ansible_run(False)
            ret = obj_installer.install()
            assert ret[1] is False
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        with patch.object(os.path, 'isfile', return_value=True):
            ret = obj_installer.install()
            assert ret[1] is False
