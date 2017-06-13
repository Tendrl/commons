import pytest
import maps
import __builtin__
from tendrl.commons.objects.node.atoms.cmd import Cmd
import mock
from tendrl.commons.utils.cmd_utils import UnsupportedCommandException,Command
from mock import patch
from tendrl.commons.objects import AtomExecutionFailedError


def run(*args):
    return "out", "No_Error", 1


# Testing run
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
    with patch.object(Command,"run",run) as mock_run:
        with pytest.raises(AtomExecutionFailedError):
            cmd.run()
    with pytest.raises(UnsupportedCommandException):
        cmd.parameters['Node.cmd_str'] = "Test_command"
        cmd.run()
