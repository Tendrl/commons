import logging

import gevent.event
import gevent.greenlet
import gevent.queue

LOG = logging.getLogger(__name__)


class CentralStore(gevent.greenlet.Greenlet):
    def __init__(self):
        super(CentralStore, self).__init__()
        self._complete = gevent.event.Event()

    def _run(self):
        LOG.info("Central Store listening")

        while not self._complete.is_set():
            gevent.sleep(0.1)
            continue

    def stop(self):
        self._complete.set()


class EtcdCentralStore(CentralStore):
    def __init__(self):
        super(EtcdCentralStore, self).__init__()

    def save_job(self, job):
        tendrl_ns.etcd_orm.save(job)
