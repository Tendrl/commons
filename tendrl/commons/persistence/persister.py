import logging

import gevent.event
import gevent.greenlet
import gevent.queue

LOG = logging.getLogger(__name__)


class DeferredCall(object):
    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def call_it(self):
        self.fn(*self.args, **self.kwargs)


class Persister(gevent.greenlet.Greenlet):
    def __init__(self):
        super(Persister, self).__init__()
        self._complete = gevent.event.Event()

    def _run(self):
        LOG.info("Persister listening")

        while not self._complete.is_set():
            gevent.sleep(0.1)
            continue

    def stop(self):
        self._complete.set()
