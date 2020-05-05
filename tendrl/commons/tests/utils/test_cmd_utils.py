import builtins
import maps
import mock
from mock import patch
import pytest

from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils import cmd_utils


def ansible(*args, **kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


def run(*args):
    NS.pop('publisher_id')
    raise ansible_module_runner.AnsibleExecutableGenerationFailed


def test_UnsupportedCommandException_constructor():
    exception_obj = cmd_utils.UnsupportedCommandException("test_cmd")
    assert exception_obj.message == "Command: test_cmd not supported by " \
                                    "tendrl commons"


def test_Command_constructor():
    cmd_obj = cmd_utils.Command("ls -a")
    assert isinstance(cmd_obj.attributes, dict)
    with pytest.raises(cmd_utils.UnsupportedCommandException):
        cmd_obj = cmd_utils.Command("test_cmd")


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    setattr(builtins, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    cmd_obj = cmd_utils.Command("ls -a")
    with patch.object(ansible_module_runner, 'AnsibleRunner', ansible):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            cmd_obj.run()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        cmd_obj.run()
