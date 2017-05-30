import pytest
from tendrl.commons.utils.ssh.generate_key import GenerateKey
from tendrl.commons.utils import ansible_module_runner
import mock
from mock import patch


def ansible_run(*args):
    if args[0]:
        return {"ssh_private_key":"test_ssh_private_key"},""
    elif not args[0]:
        return {"ssh_public_key":"test_ssh_public_key"},"Error"

def run(*args):
    raise ansible_module_runner.AnsibleExecutableGenerationFailed("Error")


def ansible(*args,**kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


def test_constructor():
    generate_key = GenerateKey()
    assert generate_key.attributes["name"] == "root"
    assert "group" not in generate_key.attributes
    generate_key = GenerateKey("user_name","User")
    assert generate_key.attributes["group"] == "User"


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    generate_key = GenerateKey()
    generate_key.attributes["_raw_params"] = "Error message"
    with patch.object(ansible_module_runner,'AnsibleRunner',ansible) as mock_ansible:
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            ret =generate_key.run()
    with patch.object(ansible_module_runner.AnsibleRunner,'run') as mock_run:
        mock_run.return_value = ansible_run(True)
        ret = generate_key.run()
    with patch.object(ansible_module_runner.AnsibleRunner,'run') as mock_run:
        mock_run.return_value = ansible_run(False)
        ret = generate_key.run()
    
