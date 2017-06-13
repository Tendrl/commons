import pytest
from tendrl.commons.utils.ssh.authorize_key import AuthorizeKey
from tendrl.commons.utils import ansible_module_runner
import mock
import maps
import __builtin__
from mock import patch


def ansible_run(*args):
    if args[0]:
        return {"msg":"test_msg"},""
    else:
        return "failed:ssh key not found","Error"

def run(*args):
    raise ansible_module_runner.AnsibleExecutableGenerationFailed("Error")


def ansible(*args,**kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


def test_constructor():
    authorize_key = AuthorizeKey("ssh-rsa")
    assert authorize_key.attributes["user"] == "root"
    assert authorize_key.attributes["key"] == "ssh-rsa"
    authorize_key = AuthorizeKey("ssh-rsa","user_name")
    assert authorize_key.attributes["user"] == "user_name"


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
    authorize_key = AuthorizeKey("ssh-rsa","user_name")
    authorize_key.attributes["_raw_params"] = "test_params"
    with patch.object(ansible_module_runner,'AnsibleRunner',ansible) as mock_ansible:
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            ret = authorize_key.run()
    with patch.object(ansible_module_runner.AnsibleRunner,'run',run) as mock_run:
        ret = authorize_key.run()
        assert ret[0] is False
    with patch.object(ansible_module_runner.AnsibleRunner,'run') as mock_run:
        mock_run.return_value = ansible_run(True)
        ret = authorize_key.run()
        assert ret[0] is True
    with patch.object(ansible_module_runner.AnsibleRunner,'run') as mock_run:
        mock_run.return_value = ansible_run(False)
        ret = authorize_key.run()
        assert ret[0] is False
