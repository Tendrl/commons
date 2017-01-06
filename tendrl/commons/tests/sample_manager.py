import gevent.event

from mock import MagicMock


class SampleManager(object):
    """sample manager for mocking

    """

    def __init__(self, integration_id):
        self._complete = gevent.event.Event()
        self._config = MagicMock()
        self.integration_id = integration_id

    def stop(self):
        pass

    def _recover(self):
        pass

    def start(self):
        pass

    def join(self):
        pass
