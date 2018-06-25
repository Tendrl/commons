import __builtin__
import datetime
import etcd
import importlib
import maps
import mock
from mock import patch
from pytz import utc


from tendrl.commons.jobs import JobConsumerThread
from tendrl.commons.objects.job import Job
from tendrl.commons.jobs import process_job
from tendrl.commons.tests.fixtures.client import Client
from tendrl.commons.tests.fixtures.ns import NameSpace
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import time_utils



test_job = JobConsumerThread()


def read_value(*args, **kwargs):
    test_job._complete._Event__flag = True
    return maps.NamedDict(
        leaves=[maps.NamedDict(key="test/job")], value="Test Value")


def read_none(*args, **kwargs):
    test_job._complete._Event__flag = True
    return maps.NamedDict(leaves=[maps.NamedDict(key="test/job")], value=False)


def read(*args, **kwargs):
    test_job._complete._Event__flag = True
    if args[0] == "/queue":
        raise etcd.EtcdKeyNotFound


status_flag = 0
status_valid = 0


def _read(*args, **kwargs):
    test_job._complete._Event__flag = True
    global status_flag
    global status_valid
    if args[1] == "/queue/job/status" and status_flag == 0:
        status_flag = 1
        return maps.NamedDict(
            leaves=[maps.NamedDict(key="test/job")], value="finished")
    elif args[1] == "/queue/job/status" and status_flag == 1:
        status_flag = 2
        return maps.NamedDict(
            leaves=[maps.NamedDict(key="test/job")], value="unfinished")
    elif args[1] == "/queue/job/status" and status_flag == 2:
        raise etcd.EtcdKeyNotFound
    elif args[1] == "/queue" or args[1] == "/queue/job/locked_by":
        return maps.NamedDict(
            leaves=[maps.NamedDict(key="test/job")], value=False)
    elif args[1] == "/queue/job/valid_until" and status_valid == 0:
        status_valid = 1
        return maps.NamedDict(
            leaves=[maps.NamedDict(key="test/job")], value=False)
    elif args[1] == "/queue/job/valid_until" and status_valid == 1:
        return maps.NamedDict(
            leaves=[
                maps.NamedDict(
                    key="test/job")],
            value=(
                time_utils.now() -
                datetime.datetime(
                    1970,
                    1,
                    1).replace(
                        tzinfo=utc)).total_seconds())


def load(*args):
    obj = importlib.import_module("tendrl.commons.tests.fixtures.client")
    obj = obj.Client()
    if args[0] == "tag":
        obj.payload = maps.NamedDict(
            type="Test_type",
            tags=["Test_tag"],
            run="tendrl.commons.objects.node.flows.test_flow",
            parameters="Test_param")
    elif args[0] == "node":
        obj.payload = maps.NamedDict(
            type="Test_type",
            tags=["Test_tag"],
            node_ids=["Test_node"],
            run="tendrl.commons.objects.node.flows.test_flow",
            parameters="Test_param")
    elif args[0] == "no_obj_name":
        obj.payload = maps.NamedDict(
            type="Test_type",
            tags=["Test_tag"],
            run="tendrl.commons.flows.test_flow",
            parameters="Test_param")
    else:
        obj.payload = maps.NamedDict(type="Test_type")
    obj.status = "new"
    obj.job_id = 1
    return obj


def write(*args, **kwargs):
    raise etcd.EtcdCompareFailed


def run(*args, **kwargs):
    raise Exception


def status_write(*args, **kwargs):
    if args[1] == "/queue/1/status" and args[2] == "finished":
        raise etcd.EtcdCompareFailed
    else:
        return True


def failed_write(*args, **kwargs):
    if args[0] == "no_err":
        return True
    if args[1] == "/queue/1/status" and args[2] == "failed":
        raise etcd.EtcdCompareFailed
    else:
        return True


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
    obj = importlib.import_module("tendrl.commons.tests.fixtures.tendrlcontext"
                                  )
    NS.tendrl_context = obj.TendrlContext()
    NS.publisher_id = "node_context"


def test_constructor():
    test_job = JobConsumerThread()
    assert not test_job._complete._Event__flag


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('time.sleep',
            mock.Mock(return_value=True))
@mock.patch('tendrl.commons.objects.BaseObject.__init__',
            mock.Mock(return_value=True))
def test_run():
    init()
    NS.node_context.fqdn = "Test"
    NS.node_context.node_id = "1"
    obj = importlib.import_module("tendrl.commons.tests.fixtures.ns")
    NS.commons = maps.NamedDict(ns=obj.NameSpace())
    with patch.object(Client, 'read', read_value):
        with patch.object(etcd_utils, 'read', read):
            global test_job
            test_job.run()
            test_job._complete._Event__flag = False
    with patch.object(Job, "load", load):
        with patch.object(Client, 'read', read_none):
            global test_job
            NS.type = "Test_type"
            test_job.run()
            test_job._complete._Event__flag = False
    with patch.object(Job, "load", load):
        with patch.object(Client, 'read', read_value):
            with patch.object(etcd_utils, 'read', read):
                global test_job
                test_job.run()
                test_job._complete._Event__flag = False
    with patch.object(Job, "load", load):
        with patch.object(Client, 'read', _read):
            global test_job
            test_job.run()
            test_job._complete._Event__flag = False
    with patch.object(Job, "load", load):
        with patch.object(Client, 'read', _read):
            global test_job
            NS.node_context.tags = "tendrl/monitor"
            test_job.run()
            test_job._complete._Event__flag = False
    with patch.object(Job, "load", load):
        with patch.object(Client, 'read', _read):
            global test_job
            NS.node_context.tags = "tendrl/monitor"
            test_job.run()
            test_job._complete._Event__flag = False
    with patch.object(Job, "load", load):
        with patch.object(Client, 'read', _read):
            global test_job
            NS.node_context.tags = "tendrl/monitor"
            test_job.run()
            test_job._complete._Event__flag = False
            with patch.object(Client, 'write', write):
                test_job.run()
                test_job._complete._Event__flag = False
            NS.node_context.tags = ""
            NS.type = "Test"
            test_job.run()
            test_job._complete._Event__flag = False
    with patch.object(Job, "load") as mock_load:
        mock_load.return_value = load("tag")
        with patch.object(Client, 'read', _read):
            global test_job
            NS.type = "Test_type"
            NS.node_context.tags = "No_tag"
            test_job.run()
            test_job._complete._Event__flag = False
            NS.node_context.tags = "Test_tag"
            test_job.run()
            test_job._complete._Event__flag = False
            mock_load.return_value = load("node")
            NS.node_context.node_id = "Test_node"
            test_job.run()
            test_job._complete._Event__flag = False
            mock_load.return_value = load("no_obj_name")
            test_job.run()
            test_job._complete._Event__flag = False
            with patch.object(Client, "write", write):
                test_job.run()
                test_job._complete._Event__flag = False
            with patch.object(Client, "write", status_write):
                test_job.run()
                test_job._complete._Event__flag = False
            with patch.object(Client, "write", failed_write):
                with patch.object(NameSpace, "run", run):
                    test_job.run()
                    test_job._complete._Event__flag = False
            with patch.object(Client, "write", failed_write("no_err")):
                with patch.object(NameSpace, "run", run):
                    test_job.run()
                    test_job._complete._Event__flag = False
    test_job = JobConsumerThread()
    test_job._complete._Event__flag = True
    test_job.run()
    NS.node_context.tags = "tendrl/monitor"
    test_job._complete._Event__flag = True
    test_job.run()


def test_stop():
    test_job = JobConsumerThread()
    test_job.stop()
    assert test_job._complete._Event__flag

def test_process_job():
    process_job(1)