import time

import etcd


from tendrl.commons import objects
from tendrl.commons.utils import log_utils as logger


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

            if _cluster.exists() and _cluster.is_managed == "yes":
                return True

            retry_count += 1
            time.sleep(1)
            if retry_count == 600:
                logger.log(
                    "error",
                    NS.publisher_id,
                    {"message": "Cluster data sync still incomplete. "
                                "Timing out"},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                    integration_id=NS.tendrl_context.integration_id
                )
                return False
