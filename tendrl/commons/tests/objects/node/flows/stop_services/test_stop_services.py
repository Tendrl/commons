import __builtin__
import etcd
import maps
import mock
from mock import patch

from tendrl.commons.objects.node.flows.stop_services import \
    StopServices
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS
from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils import log_utils as logger


def read(*args, **kwargs):
    if args:
        if args[0] == "nodes/Test_node/Os":
            raise etcd.EtcdKeyNotFound
    else:
        return None


def service_success(param):
    return None, '', 0


def service_failed(param):
    return 'error', '', 0


def mock_log(*args, **kwargs):
    pass


@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
def init(patch_get_node_id, patch_read, patch_client):
    patch_get_node_id.return_value = 1
    patch_read.return_value = etcd.Client()
    patch_client.return_value = etcd.Client()
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS._int.wclient = etcd.Client(**NS._int.etcd_kwargs)
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    NS.config.data['logging_socket_path'] = "test"
    NS.publisher_id = "node_context"
    NS.config.data['etcd_port'] = 8085
    NS.config.data['etcd_connection'] = "Test Connection"
    tendrlNS = TendrlNS()
    return tendrlNS


def test_constructor():
    init()
    StopServices()


@mock.patch(
    'tendrl.commons.event.Event.__init__',
    mock.Mock(return_value=None)
)
@mock.patch(
    'tendrl.commons.message.Message.__init__',
    mock.Mock(return_value=None)
)
def test_run():
    init()
    obj = StopServices()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters['job_id'] = "sample_uuid"
    obj.parameters['flow_id'] = "sample_uuid_1"
    obj.parameters["Services[]"] = ["TestService"]
    with patch.object(logger, 'log', mock_log):
        with patch.object(cmd_utils.Command, 'run', service_success):
            ret_val = obj.run()
            assert ret_val is True
    with patch.object(logger, 'log', mock_log):
        with patch.object(cmd_utils.Command, 'run', service_failed):
            ret_val = obj.run()
            assert ret_val is False
