from tendrl.commons.sds_sync import SdsSyncThread


class test_StateSyncThread(SdsSyncThread):
    def __init__(self):
        super(test_StateSyncThread, self).__init__()

    def run(self):
        pass

    def stop(self):
        super(test_StateSyncThread, self).stop()


def test_statesyncthread_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    obj = test_StateSyncThread()
    obj.start()
    # check thread is alive
    assert obj._complete.isSet() is False
    # check thread is not alive
    obj.stop()
    assert obj._complete.isSet() is True
