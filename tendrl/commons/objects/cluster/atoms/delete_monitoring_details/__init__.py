import time
import uuid

from tendrl.commons import objects
from tendrl.commons.utils import log_utils as logger


class DeleteMonitoringDetails(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(DeleteMonitoringDetails, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        _job_id = str(uuid.uuid4())
        payload = {
            "tags": ["tendrl/integration/monitoring"],
            "run": "monitoring.flows.DeleteMonitoringData",
            "status": "new",
            "parameters": self.parameters,
            "parent": self.parameters['job_id'],
            "type": "monitoring"
        }
        logger.log(
            "info",
            NS.publisher_id,
            {
                "message": "Creating job for monitoring integration to delete"
                           " monitoring data."
            },
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id'],
        )
        NS.tendrl.objects.Job(
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
                        "message": "Clearing monitoring data for cluster "
                        "(%s) not yet complete. Timing out." %
                        NS.tendrl.objects.Cluster(
                            integration_id=integration_id
                        ).load().short_name
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
                return False
            time.sleep(5)
            finished = True
            job = NS.tendrl.objects.Job(job_id=_job_id).load()
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
            _msg = "Child job failed %s" % _job_id
            logger.log(
                "error",
                NS.publisher_id,
                {"message": _msg},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return False
        return True
