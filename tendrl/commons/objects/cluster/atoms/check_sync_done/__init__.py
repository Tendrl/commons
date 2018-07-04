import time

from tendrl.commons import objects
from tendrl.commons.utils import log_utils as logger


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
                logger.log(
                    "error",
                    NS.publisher_id,
                    {"message": "Timing out import job, Cluster data still "
                                "not fully updated (node: %s) "
                                "(integration_id: %s)"
                                % (integration_id, NS.node_context.node_id)
                     },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                return False
            time.sleep(5)
            _cnc = NS.tendrl.objects.ClusterNodeContext(
                node_id=NS.node_context.node_id
            ).load()
            if _cnc.first_sync_done is not None and \
                    _cnc.first_sync_done.lower() == "yes":
                break
            loop_count += 1
        return True
