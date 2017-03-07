import abc
import logging

import six

from tendrl.commons import jobs

LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Manager(object):
    def __init__(
            self,
            sds_sync_thread,
            central_store_thread,
            message_handler_thread=None,
    ):
        self._central_store_thread = central_store_thread
        self._sds_sync_thread = sds_sync_thread
        self._job_consumer_thread = jobs.JobConsumerThread()
        self._message_handler_thread = message_handler_thread

    def stop(self):
        LOG.debug("%s stopping" % self.__class__.__name__)
        if self._message_handler_thread is not None:
            self._message_handler_thread.stop()
        self._job_consumer_thread.stop()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.stop()
        self._central_store_thread.stop()

    def start(self):
        LOG.debug("%s starting" % self.__class__.__name__)
        if self._message_handler_thread is not None:
            self._message_handler_thread.start()
        self._central_store_thread.start()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.start()
        self._job_consumer_thread.start()

    def join(self):
        LOG.debug("%s joining" % self.__class__.__name__)
        if self._message_handler_thread is not None:
            self._message_handler_thread.join()
        self._job_consumer_thread.join()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.join()
        self._central_store_thread.join()
