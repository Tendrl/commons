import logging

import gevent.event
import gevent.greenlet
import gevent.queue

LOG = logging.getLogger(__name__)


class deferred_call(object):
    def __init__(self, fn, args, kwargs):
        self.fn = fn
        self.args = args
        self.kwargs = kwargs

    def call_it(self):
        self.fn(*self.args, **self.kwargs)


class Persister(gevent.greenlet.Greenlet):
    def __init__(self, config):
        super(Persister, self).__init__()
        self._queue = gevent.queue.Queue()
        self._complete = gevent.event.Event()
        self._config = config

    def __get_attribute__(self, item):
        if item.startswith('_'):
            return object.__getattribute__(self, item)
        else:
            try:
                return object.__getattribute__(self, item)
            except AttributeError:
                try:
                    attr = object.__getattribute__(self, "_%s" % item)
                    if callable(attr):
                        def defer(*args, **kwargs):
                            dc = deferred_call(attr, args, kwargs)
                            try:
                                dc.call_it()
                            except Exception as ex:
                                LOG.exception(
                                    "Persister exception persisting "
                                    "data: %s" % (dc.fn,)
                                )
                                LOG.exception(ex)

                        return defer
                    else:
                        return object.__getattribute__(self, item)
                except AttributeError:
                    return object.__getattribute__(self, item)

    def _run(self):
        LOG.info("Persister listening")

        while not self._complete.is_set():
            gevent.sleep(0.1)
            pass

    def stop(self):
        self._complete.set()
