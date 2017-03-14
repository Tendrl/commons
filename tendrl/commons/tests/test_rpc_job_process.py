import sys

import gevent.event
from mock import MagicMock

from sample_manager import SampleManager

sys.modules['tendrl.commons.config'] = MagicMock()

from tendrl.commons import jobs


class Test_EtcdRpc(object):
    def test_constructor(self, monkeypatch):
        def mock_config_get(package, parameter):
            if parameter == "etcd_port":
                return 2379
            elif parameter == "etcd_connection":
                return "0.0.0.0"

        manager = SampleManager("aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6")
        monkeypatch.setattr(manager._config, 'get', mock_config_get)

    def test_stop(self):
        assert True


class TestRpcJobProcessThread(object):
    def test_etcdthread_constructor(self):
        user_request_thread = jobs.JobConsumerThread()
        assert isinstance(user_request_thread._complete, gevent.event.Event)
        assert isinstance(user_request_thread._server, jobs.JobConsumer)

    def test_etcdthread_stop(self):
        user_request_thread = jobs.JobConsumerThread()
        assert not user_request_thread._complete.is_set()

        user_request_thread.stop()

        assert user_request_thread._complete.is_set()

    def test_etcdthread_run(self, monkeypatch):
        user_request_thread = jobs.JobConsumerThread()

        user_request_thread._complete.set()
        user_request_thread._run()

        user_request_thread2 = jobs.JobConsumerThread()

        user_request_thread2.EXCEPTION_BACKOFF = 1

        def mock_server_run():
            raise Exception

        monkeypatch.setattr(user_request_thread._server,
                            'run', mock_server_run)

        assert True
