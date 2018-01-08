import etcd
import time
import uuid

from tendrl.commons import objects
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import log_utils as logger


class StopMonitoringServices(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(StopMonitoringServices, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']

        try:
            # Get the cluster nodes
            nodes = NS._int.client.read("/clusters/%s/nodes" % integration_id)
            child_job_ids = []
            node_ids = []
            for node in nodes.leaves:
                node_id = node.key.split("/")[-1]
                node_ids.append(node_id)
                # Create jobs on nodes for stoping services
                _job_id = str(uuid.uuid4())
                params = {
                    "Services[]": ["collectd"]
                }
                payload = {
                    "tags": ["tendrl/node_%s" % node_id],
                    "run": "tendrl.objects.Node.flows.StopServices",
                    "status": "new",
                    "parameters": params,
                    "parent": self.parameters["job_id"],
                    "type": "node"
                }
                Job(
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
                        "on node %s of cluster %s" %
                        (_job_id, node_id, integration_id)
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )

            # Wait for (no of nodes) * 10 secs for stop service job to complete
            loop_count = 0
            wait_count = (len(child_job_ids)) * 2
            while True:
                if loop_count >= wait_count:
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {
                            "message": "Stop service jobs not yet "
                            "complete on all nodes. Timing out. "
                            "(%s, %s)" %
                            (str(node_ids), integration_id)
                        },
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id'],
                    )
                    return False
                time.sleep(5)
                finished = True
                for child_job_id in child_job_ids:
                    child_job = Job(job_id=child_job_id).load()
                    if child_job.status != "finished":
                        finished = False
                        break
                if finished:
                    break
                else:
                    loop_count += 1
                    continue
        except etcd.EtcdKeyNotFound:
            pass

        return True
