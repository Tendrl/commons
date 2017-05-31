import pytest
import maps
import __builtin__
from tendrl.commons.objects.service.atoms.check_service_status import CheckServiceStatus
import mock
from mock import patch
from tendrl.commons.utils.cmd_utils import Command


def run(*args):
    return 'active','No Error',0


# Testing run
@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id =1
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    check_service_status = CheckServiceStatus()
    check_service_status.parameters = maps.NamedDict()
    check_service_status.parameters['Service.name'] = "Test_service"
    check_service_status.parameters['job_id'] = "node_job"
    check_service_status.parameters['flow_id'] = "flow_id"
    check_service_status.parameters['fqdn'] = "Test_fqdn"
    with patch.object(Command,"run") as mock_run:
        mock_run.return_value = run()
        ret = check_service_status.run()
        assert ret is True
    ret = check_service_status.run()
    assert ret is False
