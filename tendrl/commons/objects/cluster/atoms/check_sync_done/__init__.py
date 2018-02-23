import etcd
import time

from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError


class CheckSyncDone(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(CheckSyncDone, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']

        # wait for 360 sec to complete the first round of sync of
        # cluster data
        loop_count = 0
        while True:
            if loop_count >= 72:
                raise AtomExecutionFailedError(
                    "Timing out import job, Cluster data still not fully updated (node: %s) "
                    "(integration_id: %s)" % (
                        integration_id,
                        NS.node_context.node_id
                    )
                )
            time.sleep(5)
            try:
                _cnc = NS.tendrl.objects.ClusterNodeContext(
                    node_id=NS.node_context.node_id
                ).load()
                if _cnc.first_sync_done is not None and \
                    _cnc.first_sync_done.lower() == "yes":
                    break
            except etcd.EtcdKeyNotFound:
                loop_count += 1
                continue
        return True
