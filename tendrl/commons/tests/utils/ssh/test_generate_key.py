import __builtin__
import maps
import mock
from mock import patch
import pytest

from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils.ssh.generate_key import GenerateKey


def ansible_run(*args):
    if args[0]:
        return {"ssh_private_key": "test_ssh_private_key"}, ""
    elif not args[0]:
        return {"ssh_public_key": "test_ssh_public_key"}, "Error"


def run(*args):
    raise ansible_module_runner.AnsibleExecutableGenerationFailed("Error")


def ansible(*args, **kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_constructor():
    generate_key = GenerateKey()
    assert generate_key.attributes["name"] == "root"
    assert "group" not in generate_key.attributes
    generate_key = GenerateKey("user_name", "User")
    assert generate_key.attributes["group"] == "User"


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    generate_key = GenerateKey()
    generate_key.attributes["_raw_params"] = "Error message"
    with patch.object(ansible_module_runner, 'AnsibleRunner', ansible):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            generate_key.run()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run') as mock_run:
        mock_run.return_value = ansible_run(True)
        generate_key.run()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run') as mock_run:
        mock_run.return_value = ansible_run(False)
        generate_key.run()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        generate_key.run()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run') as mock_run:
        mock_run.return_value = None, "Test error"
        generate_key.run()
