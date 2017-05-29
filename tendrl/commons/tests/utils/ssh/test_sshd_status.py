import pytest
from tendrl.commons.utils.ssh import sshd_status
from tendrl.commons.utils import cmd_utils
import mock
from mock import patch
import maps
import psutil


def run(*args):
    return 'LoadState=loaded','No Error',0


def conn(*args):
    if args[0]:
        con = maps.NamedDict(status='LISTEN',
                             laddr = ["0.0.0.0","25"])
    else:
        con = maps.NamedDict(status='READ',
                             laddr = ["0.0.0.0","25"])
    return [con]


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_find_status():
    with patch.object(psutil.Process,'connections') as mock_connections:
        mock_connections.return_value = conn(True)
        sshd_status.find_status()
    with patch.object(psutil.Process,'connections') as mock_connections:
        mock_connections.return_value = conn(False)
        sshd_status.find_status()
    with patch.object(sshd_status,'_find_pid',return_value =0) as mock_find_pid:
        sshd_status.find_status()
    with patch.object(cmd_utils.Command,"run",run) as mock_run:
        sshd_status.find_status()


def test_find_pid():
    cmd = cmd_utils.Command("systemctl show sshd.service")
    out, err, rc = cmd.run()
    sshd_status._find_pid(out)
