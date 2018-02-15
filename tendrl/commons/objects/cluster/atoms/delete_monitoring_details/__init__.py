import time
import uuid

from tendrl.commons import objects
from tendrl.commons.objects.job import Job
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
            "type": "monitoring"
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
            if loop_count >= wait_count:
                logger.log(
                    "info",
                    NS.publisher_id,
                    {
                        "message": "Clear monitoring data "
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
            if job.status != "finished":
                finished = False
            if finished:
                break
            else:
                loop_count += 1
                continue

        return True
