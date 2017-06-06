from tendrl.commons.jobs import JobConsumerThread
import sys
import etcd
import __builtin__
from mock import patch
import mock
import maps
import importlib
import gevent.event
import datetime
from tendrl.commons.tests.fixtures.client import Client
from tendrl.commons.objects import BaseObject
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import time_utils
from pytz import utc

test_job = JobConsumerThread()

def read_value(*args,**kwargs):
    test_job._complete._flag = True
    return maps.NamedDict(leaves = [maps.NamedDict(key = "test/job")],value = "Test Value")


def read_none(*args,**kwargs):
    test_job._complete._flag = True
    return maps.NamedDict(leaves = [maps.NamedDict(key = "test/job")],value = False)

def read(*args,**kwargs):
    test_job._complete._flag = True
    if args[1] == "/queue":
        raise etcd.EtcdKeyNotFound

status_flag = 0
status_valid = 0
def _read(*args,**kwargs):
    test_job._complete._flag = True
    global status_flag
    global status_valid
    if args[1] == "/queue/job/status" and status_flag == 0:
        status_flag = 1
        return maps.NamedDict(leaves = [maps.NamedDict(key = "test/job")],value = "finished")
    elif args[1] == "/queue/job/status" and status_flag == 1:
        status_flag = 2
        return maps.NamedDict(leaves = [maps.NamedDict(key = "test/job")],value = "unfinished")
    elif args[1] == "/queue/job/status" and status_flag == 2:
        raise etcd.EtcdKeyNotFound
    elif args[1] == "/queue" or args[1] == "/queue/job/locked_by":
        return maps.NamedDict(leaves = [maps.NamedDict(key = "test/job")],value = False)
    elif args[1] == "/queue/job/valid_until" and status_valid == 0:
        status_valid = 1
        return maps.NamedDict(leaves = [maps.NamedDict(key = "test/job")],value = False)
    elif args[1] == "/queue/job/valid_until" and status_valid == 1:
        return maps.NamedDict(leaves = [maps.NamedDict(key = "test/job")],value = (time_utils.now() - datetime.datetime(1970,1,1).replace(tzinfo=utc)).total_seconds())

def load(*args):
    obj = importlib.import_module("tendrl.commons.tests.fixtures.client")
    obj = obj.Client()
    obj.payload=maps.NamedDict(type = "Test_type")
    obj.status = "new"
    obj.tags = ["test_tag"]
    obj.node_ids=["1"]
    obj.job_id = 1
    return obj
   


def init():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    obj = importlib.import_module("tendrl.commons.tests.fixtures.client")
    NS._int.client = obj.Client()
    NS._int.wclient = obj.Client()
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    obj = importlib.import_module("tendrl.commons.tests.fixtures.nodecontext")
    NS.node_context = obj.NodeContext()
    NS.publisher_id = "node_context"

def test_constructor():
    test_job = JobConsumerThread()
    assert not test_job._complete._flag


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('gevent.sleep',
            mock.Mock(return_value=True))
@mock.patch('tendrl.commons.objects.BaseObject.__init__',
            mock.Mock(return_value=True))
def test_run():
    init()
    NS.node_context.node_id = "1"
    with patch.object(Client,'read',read_value) as mock_read:
         global test_job
         test_job._run()
         test_job._complete._flag = False
    with patch.object(Job,"load",load) as mock_load:
        with patch.object(Client,'read',read_none) as mock_read:
             global test_job
             NS.type = "Test_type"
             test_job._run()
             test_job._complete._flag = False
    with patch.object(Job,"load",load) as mock_load:
        with patch.object(Client,'read',read) as mock_read:
             global test_job
             test_job._run()
             test_job._complete._flag = False
    with patch.object(Job,"load",load) as mock_load:
        with patch.object(Client,'read',_read) as mock_read:
             global test_job
             test_job._run()
             test_job._complete._flag = False
    with patch.object(Job,"load",load) as mock_load:
        with patch.object(Client,'read',_read) as mock_read:
             global test_job
             NS.node_context.tags = "tendrl/monitor"
             test_job._run()
             test_job._complete._flag = False
    with patch.object(Job,"load",load) as mock_load:
        with patch.object(Client,'read',_read) as mock_read:
             global test_job
             NS.node_context.tags = "tendrl/monitor"
             test_job._run()
             test_job._complete._flag = False
    test_job = JobConsumerThread()
    test_job._complete._flag = True
    test_job._run()
    NS.node_context.tags = "tendrl/monitor"
    test_job._complete._flag = True
    test_job._run()
    
