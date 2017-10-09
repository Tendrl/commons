import abc
import threading

import six


@six.add_metaclass(abc.ABCMeta)
class StateSyncThread(threading.Thread):
    def __init__(self):
        super(StateSyncThread, self).__init__()

        self._complete = threading.Event()

    def stop(self):
        self._complete.set()

    @abc.abstractmethod
    def run(self):
        raise NotImplementedError(
            'define the function run to use this class'
        )


@six.add_metaclass(abc.ABCMeta)
class SdsSyncThread(StateSyncThread):
    def __init__(self):
        super(SdsSyncThread, self).__init__()
