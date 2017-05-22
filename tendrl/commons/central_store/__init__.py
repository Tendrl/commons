import gevent.event
import gevent.greenlet
import gevent.queue

from tendrl.commons.event import Event
from tendrl.commons.message import Message


class CentralStore(gevent.greenlet.Greenlet):
    def __init__(self):
        super(CentralStore, self).__init__()
        self._complete = gevent.event.Event()

    def _run(self):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Central Store listening"}
            )
        )
        while not self._complete.is_set():
            gevent.sleep(30)

    def stop(self):
        self._complete.set()


class EtcdCentralStore(CentralStore):
    def __init__(self):
        super(EtcdCentralStore, self).__init__()
        
