import gevent
import pytest

from tendrl.commons.sds_sync import SdsSyncThread
from tendrl.commons.sds_sync import StateSyncThread


class test_StateSyncThread(StateSyncThread):
    def __init__(self):
        super(test_StateSyncThread, self).__init__()

    def _run(self):
        super(test_StateSyncThread, self)._run()

    def stop(self):
        super(test_StateSyncThread, self).stop()


class test_SdsSyncThread(SdsSyncThread):
    def __init__(self):
        super(test_SdsSyncThread, self).__init__()

    def _run(self):
        super(test_SdsSyncThread, self)._run()
# Testing StateSyncThread __init__


def test_statesyncthread_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    assert isinstance(test_StateSyncThread()._complete, gevent.event.Event)


def test_run():
    with pytest.raises(NotImplementedError):
        test_StateSyncThread()._run()


def test_stop():
    test_StateSyncThread().stop()
    # assert test_StateSyncThread()._complete.isset()


def test_sdssyncthread_constructor():
    with pytest.raises(NotImplementedError):
        test_SdsSyncThread()._run()
