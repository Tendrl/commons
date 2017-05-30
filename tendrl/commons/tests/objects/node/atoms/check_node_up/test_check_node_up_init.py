import pytest
import maps
import __builtin__
from tendrl.commons.objects.node.atoms.check_node_up import CheckNodeUp
import mock
from mock import patch
from tendrl.commons.utils.cmd_utils import Command

def run(*args):
    return "Test Out", '', 0    

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
    check_node_up = CheckNodeUp()
    check_node_up.parameters = maps.NamedDict()
    check_node_up.parameters['fqdn'] = "www.google.com"
    check_node_up.parameters['job_id'] = "node_job"
    check_node_up.parameters['flow_id'] = "flow_id"
    check_node_up.run()
    with patch.object(Command,"run",run) as mock_run:
        check_node_up.run()
    check_node_up.parameters['fqdn'] = "Test_fqdn"
    check_node_up.run()
