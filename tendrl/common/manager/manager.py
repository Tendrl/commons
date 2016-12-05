import abc
import greenlet
import gevent.event
import gevent.greenlet

from tendrl.common.manager.rpc import EtcdThread
from tendrl.gluster_integration.persistence.persister import Persister


class TopLevelEvents(gevent.greenlet.Greenlet):
    __metaclass__ = abc.ABCMeta

    def __init__(self, manager):
        super(TopLevelEvents, self).__init__()

        self._manager = manager
        self._complete = gevent.event.Event()

    def stop(self):
        self._complete.set()

    @abc.abstractmethod
    def _run(self):
        raise NotImplementedError(
            'define the function on_pull to use this class'
        )


class Manager(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, name, integration_id, config, events, persister, defs_dir):
        self.name = name
        self._config = config
        self.integration_id = integration_id
        self._complete = gevent.event.Event()
        self._user_request_thread = EtcdThread(self)
        self._discovery_thread = events
        self.persister = persister
        self.defs_dir = defs_dir

    def stop(self):
        LOG.info("%s stopping" % self.__class__.__name__)
        self._user_request_thread.stop()
        self._discovery_thread.stop()

    def _recover(self):
        LOG.debug("Recovered server")
        pass

    def start(self):
        LOG.info("%s starting" % self.__class__.__name__)
        self._user_request_thread.start()
        self._discovery_thread.start()
        self.persister.start()

    def join(self):
        LOG.info("%s joining" % self.__class__.__name__)
        self._user_request_thread.join()
        self._discovery_thread.join()
        self.persister.join()

    @abc.abstractmethod
    def on_pull(self, raw_data, cluster_id):
        raise NotImplementedError(
            'define the function on_pull to use this class'
        )
