import etcd
import maps
from mock import MagicMock
from mock import patch
import threading
import time
import mock
import uuid


from tendrl.commons.jobs import JobConsumerThread
from tendrl.commons.objects.job import Job
from tendrl.commons.jobs import process_job
from tendrl.commons.tests.fixtures.client import Client
from tendrl.commons.tests.fixtures.ns import NameSpace
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import time_utils



test_job = JobConsumerThread()

from tendrl.commons import jobs
from tendrl.commons.objects import BaseObject
from tendrl.commons.tests import test_init
from tendrl.commons.utils import alert_utils
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


JOB_SET = True


def is_set():
    global JOB_SET
    JOB_SET = not JOB_SET
    return JOB_SET


def read(param):
    key = "/queue/%s/locked_by" % "808a4162-4b70-4ff0-b218-45dbe371e545"
    if param == key:
        raise etcd.EtcdKeyNotFound


def test_constructor():
    test_job = jobs.JobConsumerThread()
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
    NS.node_context.node_id = str(uuid.uuid4())
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

@patch.object(threading, "Thread")
@patch.object(time, "sleep")
@patch.object(etcd_utils, "read", read)
@patch.object(BaseObject, "load_all")
def test_job_consumer_thread(load_all, sleep, thread):
    test_init.init()
    thread.return_value = MagicMock()
    sleep.return_value = None
    job = NS.tendrl.objects.Job(
        job_id="808a4162-4b70-4ff0-b218-45dbe371e545",
        status="new",
        payload={"status": "new"}
    )
    load_all.return_value = [job]
    NS.publisher_id = "testing"
    obj = jobs.JobConsumerThread()
    with patch.object(NS.node_context, "load") as nc_load:
        NS.node_context.fqdn = "tendrl-node-1"
        nc_load.return_value = NS.node_context
        with patch.object(NS.tendrl_context, "load") as tc_load:
            with patch.object(obj._complete, "is_set", is_set):
                NS.tendrl_context.integration_id = \
                    "b0b18359-3444-40b7-aa99-853f1b7308de"
                tc_load.return_value = NS.tendrl_context
                obj.run()


@patch.object(logger, "log")
def test_process_job_fail(log):
    # no tag match
    test_init.init()
    NS.type = "node"
    NS.publisher_id = "pytest"
    NS.tendrl.objects.Job.load = MagicMock()
    job = NS.tendrl.objects.Job(
        job_id="808a4162-4b70-4ff0-b218-45dbe371e545",
        payload={"status": "new", "type": "node"}
    )
    NS.tendrl.objects.Job.load.return_value = job
    with patch.object(job, "save") as save:
        save.return_value = None
        with patch.object(NS.node_context, "load") as nc_load:
            nc_load.return_value = NS.node_context
            jobs.process_job("808a4162-4b70-4ff0-b218-45dbe371e545")
            log.assert_called_with(
                'debug',
                'pytest',
                {'message': u"Node (test_node_id)(type: node)"
                 "(tags: [u'my_tag']) will not process "
                 "job-808a4162-4b70-4ff0-b218-45dbe371e545 (tags: )"}
            )


@patch.object(alert_utils, "alert_job_status")
@patch.object(jobs, "_extract_fqdn")
@patch.object(etcd_utils, "write")
@patch.object(logger, "log")
def test_process_job_pass(log, write, extract_fqdn, alert_util):
    test_init.init()
    NS.get_obj_flow = MagicMock()
    curr_ns = maps.NamedDict(ns=NS)
    extract_fqdn.return_value = (curr_ns, "import", "cluster")
    write.return_value = None
    NS.type = "node"
    NS.publisher_id = "pytest"
    NS.tendrl.objects.Job.load = MagicMock()
    job = NS.tendrl.objects.Job(
        job_id="808a4162-4b70-4ff0-b218-45dbe371e545",
        payload={"status": "new",
                 "type": "node",
                 "tags": ["testing"],
                 "run": "testing",
                 "parameters": {"flow_id": ""}}
    )
    job.locked_by = dict(node_id=NS.node_context.node_id,
                         fqdn=NS.node_context.fqdn,
                         tags=NS.node_context.tags,
                         type=NS.type)
    NS.node_context.tags = ["testing"]
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = None
    NS.tendrl_context.cluster_name = None
    NS.tendrl.objects.Job.load.return_value = job
    NS.config = maps.NamedDict()
    NS.config.data = maps.NamedDict()
    NS.config.data.logging_socket_path = "tests/path"
    with patch.object(job, "save") as save:
        save.return_value = None
        with patch.object(NS.node_context, "load") as nc_load:
            nc_load.return_value = NS.node_context
            jobs.process_job("808a4162-4b70-4ff0-b218-45dbe371e545")
            alert_util.assert_called_with(
                'finished',
                'testing (job ID: 808a4162-4b70-4ff0-b218-45dbe371e545) '
                'completed successfully ',
                cluster_name=None,
                integration_id=None
            )
