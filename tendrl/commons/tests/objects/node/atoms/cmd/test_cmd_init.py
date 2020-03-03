import builtins
import maps
import mock
from mock import patch
import pytest

from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects.node.atoms.cmd import Cmd
from tendrl.commons.utils.cmd_utils import Command
from tendrl.commons.utils.cmd_utils import UnsupportedCommandException


def run(*args):
    return "out", "No_Error", 1


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    cmd = Cmd()
    cmd.parameters = maps.NamedDict()
    cmd.parameters['fqdn'] = "Test"
    cmd.parameters['Node.cmd_str'] = "lscpu"
    cmd.parameters['job_id'] = "node_job"
    cmd.parameters['flow_id'] = "flow_id"
    cmd.run()
    with patch.object(Command, "run", run):
        with pytest.raises(AtomExecutionFailedError):
            cmd.run()
    with pytest.raises(UnsupportedCommandException):
        cmd.parameters['Node.cmd_str'] = "Test_command"
        cmd.run()
