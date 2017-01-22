import abc

import gevent.event
import gevent.greenlet
import six


@six.add_metaclass(abc.ABCMeta)
class SdsSyncThread(gevent.greenlet.Greenlet):
    def __init__(self):
        super(SdsSyncThread, self).__init__()

        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    @abc.abstractmethod
    def _run(self):
        raise NotImplementedError(
            'define the function on_pull to use this class'
        )
