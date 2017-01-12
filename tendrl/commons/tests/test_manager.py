import sys

from gevent.event import Event
from mock import MagicMock

sys.modules['tendrl.commons.config'] = MagicMock()
from tendrl.commons.manager import manager
from tendrl.commons.manager.rpc_job_process import RpcJobProcessThread


class MyManager(manager.Manager):
    def __init__(
            self,
            name,
            integration_id,
            config,
            events,
            persister_thread,
            defs_dir,
            node_id=None,
    ):
        super(MyManager, self).__init__(
            name,
            integration_id,
            config,
            events,
            persister_thread,
            defs_dir,
            node_id=node_id,
        )

    def on_pull(self, raw_data, cluster_id):
        pass


class TestManager(object):
    def setup_method(self, method):
        self.manager = MyManager(
            "dummymodule",
            'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6',
            MagicMock(),
            MagicMock(),
            MagicMock(),
            "dummypath",
            node_id='aa22a6fe-87f0-45cf-8b70-2d0ff4c02bf7'
        )

    def test_manager_constructor(self):
        assert isinstance(
            self.manager._rpc_job_process_thread,
            RpcJobProcessThread
        )
        assert isinstance(
            self.manager._complete,
            Event
        )

    def test_manager_stop(self, monkeypatch):
        def mock_rpc_job_process_thread_stop():
            return

        monkeypatch.setattr(self.manager._rpc_job_process_thread,
                            'stop',
                            mock_rpc_job_process_thread_stop)

        def mock_persister_thread_stop():
            return

        monkeypatch.setattr(self.manager.persister_thread,
                            'stop',
                            mock_persister_thread_stop)

        self.manager.stop()
        assert True

    def test_manager_start(self, monkeypatch):
        def mock_rpc_job_process_thread_start():
            return

        monkeypatch.setattr(self.manager._rpc_job_process_thread,
                            'start',
                            mock_rpc_job_process_thread_start)

        def mock_persister_thread_start():
            return

        monkeypatch.setattr(self.manager.persister_thread,
                            'start',
                            mock_persister_thread_start)

        self.manager.start()
        assert True

    def test_manager_join(self, monkeypatch):
        def mock_rpc_job_process_thread_join():
            return

        monkeypatch.setattr(self.manager._rpc_job_process_thread,
                            'join',
                            mock_rpc_job_process_thread_join)

        def mock_persister_thread_join():
            return

        monkeypatch.setattr(self.manager.persister_thread,
                            'join',
                            mock_persister_thread_join)

        self.manager.join()
        assert True
