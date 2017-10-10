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
            message_handler_thread=None,
    ):
        self._sds_sync_thread = sds_sync_thread
        self._job_consumer_thread = jobs.JobConsumerThread()
        self._message_handler_thread = message_handler_thread

    def stop(self):
        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "%s stopping" % self.__class__.__name__}
            )
        )
        if self._message_handler_thread is not None:
            self._message_handler_thread.stop()
        self._job_consumer_thread.stop()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.stop()

    def start(self):
        Event(
            Message(
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "%s starting" % self.__class__.__name__}
            )
        )
        if self._message_handler_thread is not None:
            self._message_handler_thread.start()
        if self._sds_sync_thread is not None:
            self._sds_sync_thread.start()
        self._job_consumer_thread.start()
