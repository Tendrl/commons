import sys

from mock import MagicMock

sys.modules['tendrl.commons.config'] = MagicMock()
from tendrl.commons import jobs
from tendrl.commons import manager


class MyManager(manager.Manager):
    def __init__(
            self,
            name,
            integration_id
    ):
        super(MyManager, self).__init__(
            name,
            integration_id
        )

    def on_pull(self, raw_data, cluster_id):
        pass


class TestManager(object):
    def setup_method(self, method):
        self.manager = MyManager(
            "dummymodule",
            'aa22a6fe-87f0-45cf-8b70-2d0ff4c02af6'
        )

    def test_manager_constructor(self):
        assert isinstance(
            self.manager._job_consumer_thread,
            jobs.JobConsumerThread
        )
