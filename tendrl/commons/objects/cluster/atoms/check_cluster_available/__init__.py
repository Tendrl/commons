import etcd
import gevent

from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.utils import etcd_utils


class CheckClusterAvailable(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(CheckClusterAvailable, self).__init__(*args, **kwargs)

    def run(self):
        retry_count = 0
        while True:
            _cluster = None
            try:
                _cluster = NS.tendrl.objects.Cluster(
                    integration_id=self.parameters[
                        "TendrlContext.integration_id"
                    ]
                ).load()
            except etcd.EtcdKeyNotFound:
                # pass and continue the time out below
                pass

            if _cluster and _cluster.sync_status == "done":
                return True

            retry_count += 1
            gevent.sleep(1)
            if retry_count == 600:
                Event(
                    Message(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={
                            "message": "Cluster data sync still incomplete. Timing out"
                        },
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id'],
                        cluster_id=NS.tendrl_context.integration_id,
                    )
                )
                raise AtomExecutionFailedError(
                    "Cluster data sync still incomplete. Timing out"
                )
