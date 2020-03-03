import builtins
import maps
from mock import patch
import pytest


from tendrl.commons.flows.authorize_ssh_key import AuthorizeSshKey
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils import ansible_module_runner


'''Dummy Functions'''


def run(*args):
    return "passed", ""


'''Unit Test Cases'''


def test_constructor():
    authorize_obj = AuthorizeSshKey()
    assert authorize_obj._defs["help"] == "Authorize SSH Key"


def test_run():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.config = maps.NamedDict()
    NS.config.data = maps.NamedDict()
    NS.publisher_id = "node_context"
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    NS.config.data['logging_socket_path'] = "test"
    authorize_obj = AuthorizeSshKey()
    param = maps.NamedDict()
    param['ssh_key'] = "test_ssh_key"
    authorize_obj.parameters = param
    with pytest.raises(FlowExecutionFailedError):
        authorize_obj.run()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        ret = authorize_obj.run()
        assert ret is True
