import abc

import six

from tendrl.commons import jobs
from tendrl.commons.utils import log_utils as logger


@six.add_metaclass(abc.ABCMeta)
class Manager(object):
    def __init__(
            self,
            sds_sync_thread,
            message_handler_thread=None,
    ):
        self._sds_sync_thread = sds_sync_thread
        self._job_consumer_thread = jobs.JobConsumerThread()
        self._message_handler_thread = message_handler_thread

    def stop(self):
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": "%s stopping" % self.__class__.__name__}
        )
        if self._message_handler_thread is not None:
            self._message_handler_thread.stop()
        self._job_consumer_thread.stop()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.stop()

    def start(self):
        logger.log(
            "debug",
            NS.publisher_id,
            {"message": "%s starting" % self.__class__.__name__}
        )
        if self._message_handler_thread is not None:
            self._message_handler_thread.start()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.start()
        self._job_consumer_thread.start()
