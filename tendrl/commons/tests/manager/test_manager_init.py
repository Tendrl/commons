import __builtin__
import maps
import mock
import pytest


from tendrl.commons import jobs
from tendrl.commons.manager import Manager


def test_constructor(monkeypatch):
    """Testing for constructor involves checking if all needed

    variables are declared initialized
    """

    def job_consume():
        return "Thread Consuming Job"
    monkeypatch.setattr(jobs, 'JobConsumerThread', job_consume)
    manager = Manager("test")
    assert manager._sds_sync_thread == "test"
    assert manager._message_handler_thread is None
    assert manager._job_consumer_thread == "Thread Consuming Job"


# Testing stop
@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_stop():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    # Creating dummy job
    sds_job = jobs.JobConsumerThread()

    # Testing to stop the sds_sync thread
    manager = Manager(sds_job)
    manager.stop()
    assert manager._sds_sync_thread._complete.is_set()

    # Testing to stop all threads
    sds_job = jobs.JobConsumerThread()
    message_job = jobs.JobConsumerThread()
    manager = Manager(sds_job, message_job)
    manager.stop()
    assert manager._sds_sync_thread._complete.is_set() and \
        manager._job_consumer_thread._complete.is_set() and \
        manager._message_handler_thread._complete.is_set()
    manager = Manager(None)
    manager.stop()


# Testing start
@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_start():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"

    # Creating dummy job
    sds_job = jobs.JobConsumerThread()

    # Testing to start the sds_sync thread
    manager = Manager(sds_job)
    manager.start()
    assert manager._sds_sync_thread._complete.is_set() is False

    # Testing to start all threads
    sds_job = jobs.JobConsumerThread()
    message_job = jobs.JobConsumerThread()
    manager = Manager(sds_job, message_job)
    manager.start()
    assert manager._message_handler_thread._complete.is_set() is False
    # Testig with None Value
    manager = Manager(None)
    manager.start()
    # Testing for type of argument passed

    test_job = "Testing for failure"
    manager = Manager(test_job)
    with pytest.raises(AttributeError):
        manager.start()
