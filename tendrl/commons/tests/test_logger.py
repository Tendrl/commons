import __builtin__
import etcd
from etcd import Client
import importlib
from inspect import getframeinfo
from inspect import stack
import maps
import mock
from mock import patch
import pytest


from tendrl.commons.logger import Logger
from tendrl.commons.message import Message
from tendrl.commons.utils.time_utils import now


def getatr(*args, **kwargs):
    raise AttributeError


@patch.object(etcd, "Client")
@patch.object(Client, "refresh")
@patch.object(Client, 'write')
def init(patch_write, patch_refresh, patch_client):
    patch_write.return_value = True
    patch_refresh.return_value = True
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
    NS.config.data['message_retention_time'] = "infinite"
    NS.node_agent = maps.NamedDict()
    NS.node_agent.objects = importlib.import_module(
        "tendrl.commons.tests.fixtures.cluster_message")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    message = maps.NamedDict()
    message["priority"] = "info"
    message["integration_id"] = "test_cluster"
    message["message_id"] = "test_id"
    message["timestamp"] = now()
    message["publisher"] = "node_context"
    message["node_id"] = "test_id"
    message["payload"] = {"message": "test_message"}
    message["job_id"] = "test_job_id"
    message["flow_id"] = "test_flow_id"
    message["parent_id"] = "test_parent_id"
    obj_caller = getframeinfo(stack()[1][0])
    obj_caller = {"filename": obj_caller.filename,
                  "line_no": obj_caller.lineno,
                  "function": obj_caller.function}
    message["caller"] = obj_caller
    return message


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_constructor():
    message = init()
    log = Logger(message)
    assert log.message == message
    with patch.object(Logger, '_logger') as mock_logger:
        log = Logger(message)
        assert mock_logger.called
    message["job_id"] = None
    log = Logger(message)
    with patch.object(Logger, 'push_event') as mock_push_event:
        log = Logger(message)
        assert mock_push_event.called
    message.payload = maps.NamedDict(
        exception_traceback="Traceback",
        message="Test Message",
        exception_type="Exception Type")
    log = Logger(message)
    message["integration_id"] = None
    log = Logger(message)
    message["job_id"] = None
    message["priority"] = "notice"
    with patch.object(Logger, 'push_notification') as mock_notification:
        log = Logger(message)
        assert mock_notification.called



def test_push_event():
    message = init()
    log = Logger(message)
    message["priority"] = "error"
    log.push_event()

def test_push_notification():
    message = init()
    log = Logger(message)
    message["priority"] = "error"
    log.push_notification()


def test_push_message():
    message = init()
    log = Logger(message)
    message["priority"] = "error"
    log.push_message()
    message["integration_id"] = None
    log.push_message()


def test_logger():
    message = init()
    log = Logger(message)
    log._logger(message)
    msg = Message(priority=None, publisher="node_context",
                  payload={"message": "Test Message"})
    log._logger(msg)
    with patch.object(__builtin__, 'getattr', getatr):
        with pytest.raises(NotImplementedError):
            log._logger(msg)
