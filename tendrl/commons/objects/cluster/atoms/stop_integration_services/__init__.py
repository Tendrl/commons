import etcd
import time
import uuid

from tendrl.commons import objects
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class StopIntegrationServices(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(StopIntegrationServices, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        _cluster = NS.tendrl.objects.Cluster(
            integration_id=integration_id
        ).load()

        try:
            # Get the cluster nodes
            nodes = etcd_utils.read("/clusters/%s/nodes" % integration_id)
            child_job_ids = []
            node_ids = []
            for node in nodes.leaves:
                node_id = node.key.split("/")[-1]
                node_ids.append(node_id)
                # Create jobs on nodes for stoping services
                _job_id = str(uuid.uuid4())
                params = {
                    "Services[]": ["tendrl-gluster-integration"]
                }
                payload = {
                    "tags": ["tendrl/node_%s" % node_id],
                    "run": "tendrl.objects.Node.flows.StopServices",
                    "status": "new",
                    "parameters": params,
                    "parent": self.parameters["job_id"],
                    "type": "node"
                }
                NS.tendrl.objects.Job(
                    job_id=_job_id,
                    status="new",
                    payload=payload
                ).save()
                child_job_ids.append(_job_id)
                logger.log(
                    "info",
                    NS.publisher_id,
                    {
                        "message": "Stop tendrl services (job: %s) "
                        "on %s in cluster %s" %
                        (_job_id, node_id, _cluster.short_name)
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )

            # Wait for (no of nodes) * 10 secs for stop service job to complete
            loop_count = 0
            wait_count = (len(child_job_ids)) * 2
            while True:
                child_jobs_failed = []
                if loop_count >= wait_count:
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {
                            "message": "Stop service jobs on cluster(%s) not "
                            "yet complete on all nodes(%s). Timing out. "
                            % (_cluster.short_name, str(node_ids))
                        },
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id'],
                    )
                    return False
                time.sleep(5)
                finished = True
                for child_job_id in child_job_ids:
                    child_job = NS.tendrl.objects.Job(
                        job_id=child_job_id
                    ).load()
                    if child_job.status not in ["finished", "failed"]:
                        finished = False
                    elif child_job.status == "failed":
                        child_jobs_failed.append(child_job.job_id)
                if finished:
                    break
                else:
                    loop_count += 1
                    continue
            if len(child_jobs_failed) > 0:
                _msg = "Child jobs failed are %s" % child_jobs_failed
                logger.log(
                    "error",
                    NS.publisher_id,
                    {"message": _msg},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                return False
        except etcd.EtcdKeyNotFound:
            pass

        return True
