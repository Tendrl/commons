import abc

import six

from tendrl.commons.event import Event
from tendrl.commons.message import Message

from tendrl.commons import jobs


@six.add_metaclass(abc.ABCMeta)
class Manager(object):
    def __init__(
            self,
            sds_sync_thread,
            central_store_thread=None,
            message_handler_thread=None,
    ):
        self._central_store_thread = central_store_thread
        self._sds_sync_thread = sds_sync_thread
        self._job_consumer_thread = jobs.JobConsumerThread()
        self._message_handler_thread = message_handler_thread

    def stop(self):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s stopping" % self.__class__.__name__}
            )
        )
        if self._message_handler_thread is not None:
            self._message_handler_thread.stop()
        self._job_consumer_thread.stop()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.stop()
        if self._central_store_thread is not None:
            self._central_store_thread.stop()

    def start(self):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s starting" % self.__class__.__name__}
            )
        )
        if self._message_handler_thread is not None:
            self._message_handler_thread.start()
        if self._central_store_thread is not None:
            self._central_store_thread.start()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.start()
        self._job_consumer_thread.start()

    def join(self):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s joining" % self.__class__.__name__}
            )
        )
        if self._message_handler_thread is not None:
            self._message_handler_thread.join()
        self._job_consumer_thread.join()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.join()
        if self._central_store_thread is not None:
            self._central_store_thread.join()
