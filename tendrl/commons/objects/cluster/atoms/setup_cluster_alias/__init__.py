import time
import uuid

from tendrl.commons import objects
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import log_utils as logger


class SetupClusterAlias(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(SetupClusterAlias, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        if "provisioner/%s" % integration_id not in NS.node_context.tags:
            return True

        _job_id = str(uuid.uuid4())
        payload = {
            "tags": ["tendrl/integration/monitoring"],
            "run": "monitoring.flows.SetupClusterAlias",
            "status": "new",
            "parameters": self.parameters,
            "type": "monitoring",
            "parent": self.parameters['job_id']
        }
        Job(
            job_id=_job_id,
            status="new",
            payload=payload
        ).save()

        # Wait for 2 mins for the job to complete
        loop_count = 0
        wait_count = 24
        while True:
            child_job_failed = False
            if loop_count >= wait_count:
                logger.log(
                    "error",
                    NS.publisher_id,
                    {
                        "message": "Setting up cluster alias"
                        "not yet complete. Timing out. (%s)" %
                        integration_id
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
                return False
            time.sleep(5)
            finished = True
            job = Job(job_id=_job_id).load()
            if job.status not in ["finished", "failed"]:
                finished = False
            elif job.status == "failed":
                child_job_failed = True
            if finished:
                break
            else:
                loop_count += 1
                continue
        if child_job_failed:
            _msg = "Child job setting up cluster alias " \
                   "failed %s" % _job_id
            logger.log(
                "error",
                NS.publisher_id,
                {"message": _msg},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return False
        return True
