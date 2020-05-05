import builtins
import maps
import mock
from mock import patch
import psutil

from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils.ssh import sshd_status


def run(*args):
    return 'LoadState=loaded', 'No Error', 0


def conn(*args):
    if args[0]:
        con = maps.NamedDict(status='LISTEN',
                             laddr=["0.0.0.0", "25"])
    else:
        con = maps.NamedDict(status='READ',
                             laddr=["0.0.0.0", "25"])
    return [con]


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_find_status():
    setattr(builtins, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    with patch.object(psutil.Process, 'connections') as mock_connections:
        mock_connections.return_value = conn(True)
        sshd_status.find_status()
    with patch.object(psutil.Process, 'connections') as mock_connections:
        mock_connections.return_value = conn(False)
        sshd_status.find_status()
    with patch.object(sshd_status, '_find_pid', return_value=0):
        sshd_status.find_status()
    with patch.object(cmd_utils.Command, "run", run):
        sshd_status.find_status()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_find_pid():
    setattr(builtins, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    cmd = cmd_utils.Command("systemctl show sshd.service")
    out, err, rc = cmd.run()
    sshd_status._find_pid(out)
