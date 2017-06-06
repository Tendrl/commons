from tendrl.commons.flows.setup_ssh import SetupSsh
import maps
import mock
import __builtin__
import tempfile
from mock import patch


def test_constructor():
    setup_ssh = SetupSsh()
    assert setup_ssh._defs is not None


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    param = maps.NamedDict(ssh_setup_script = 'Test ssh_setup_script')
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    setup_ssh = SetupSsh(parameters = param)
    setup_ssh.run()
