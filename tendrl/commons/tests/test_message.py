import os
import pytest
import maps
import importlib
import __builtin__
import sys
import datetime
import json
from inspect import getframeinfo
from inspect import stack
import traceback

from mock import MagicMock
from tendrl.commons import message
from tendrl.commons.message import Message
from tendrl.commons.message import ExceptionMessage
from mock import patch
from tendrl.commons.utils.time_utils import now


def init():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS["node_context"] = maps.NamedDict()
    NS.node_context["node_id"] = "Test_node_id"


def test_from_json():
    init()
    json_string = '{"timestamp":"Sat Oct 11 17:13:46 UTC 2003", "priority": "info","publisher": "node_context", "payload" : { "message": "TestMessage"}}'
    msg = Message.from_json(json_string)
    assert msg.priority == "info"
    json_string = '{"timestamp":"Sat Oct 11 17:13:46 UTC 2003", "priority": "None","publisher": "node_context", "payload" : { "message": "TestMessage"}}'
    msg = Message.from_json(json_string)
    assert msg.priority == "debug"


def test_to_json():
    init()
    msg = Message("info","node_context",payload = {"message":"Test Message"})
    message = Message.to_json(msg)
    assert message.find("info")


def test_validate():
    init()
    msg = Message(priority = None,publisher = "node_context", payload = {"message":"Test Message"})
    assert msg.validate() is False
    msg = Message(priority = "info",publisher = None, payload = {"message":"Test Message"})
    assert msg.validate() is False
    msg = Message(priority = "info",publisher = "node_context", payload = '{"message":"Test Message"}')
    assert msg.validate() is False
    msg = Message(priority = "info",publisher = "node_context", payload = {"message":"Test Message"}, job_id = "test_job")
    assert msg.validate() is False
    msg = Message(priority = "info",publisher = "node_context", payload = {"message":"Test Message"}, job_id = "test_job", flow_id = "test_flow")
    assert msg.validate() is True


def test_contructor_ExceptionMessage():
    init()
    with pytest.raises(Exception):
        ex_msg = ExceptionMessage(priority = "info",publisher = "node_context", payload = {"message":"Test Exception Message"})
    ex = Exception("Test Exception")
    ex_msg = ExceptionMessage(priority = "info",publisher = "node_context", payload = {"message":"Test Exception Message","exception":ex})
    
    #ex_msg = ExceptionMessage(priority = "info",publisher = "node_context", payload = '{"message":"Test Exception Message","exception":"Test Exception"}')

def test_constructor_Messsage():
    init()
    msg = Message(priority = "info",publisher = "node_context",payload = {"message":"Test Message"})
    assert msg.priority == "info"
    assert msg.publisher == "node_context"
    assert msg.caller is not None
    assert msg.message_id is not None
    msg = Message("info","node_context", message_id = 1, timestamp = now(), payload={"message":"Test Message"})
    assert msg.message_id == 1
    assert type(msg.timestamp) is datetime.datetime
    obj_caller = getframeinfo(stack()[1][0])
    obj_caller = {"filename": obj_caller.filename,
                  "line_no": obj_caller.lineno,
                  "function": obj_caller.function}
    msg = Message("info","node_context", payload = {"message":"Test Message"}, caller = obj_caller)
    msg = Message(priority = "info", publisher = "node_context", payload = {"message":"Test Message"}, node_id = "Test id")
    assert msg.node_id == "Test id"
    #sys.path.append('/usr/lib64/collectd')
    #del(sys.modules["tendrl.commons.message"])
    #mod = importlib.import_module("tendrl.commons.message")
    #sys.path.remove('/usr/lib64/collectd')
    #del(sys.modules["tendrl.commons.message"])


def test_format_exception():
    formatted_stack = traceback.extract_stack()[:-2]
    ex = Exception("Test Exception")
    ex_msg = ExceptionMessage(priority = "info",publisher = "node_context", payload = {"message":"Test Exception Message","exception":ex})
    ex_msg.format_exception(formatted_stack)


def test_serialize_message():
    msg = Message(priority = "info",publisher = "node_context",payload = {"message":"Test Message"})
    ret = message.serialize_message(msg)
    assert type(ret) is dict
    ex = Exception("Test Exception")
    ret = message.serialize_message(ex)
    assert ret is not None
    ret = message.serialize_message(datetime.datetime.now())
    assert type(ret) is str
    with pytest.raises(TypeError):
        ret = message.serialize_message("")
