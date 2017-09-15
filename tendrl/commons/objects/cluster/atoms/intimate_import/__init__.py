import uuid

from tendrl.commons import objects
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import log_utils as logger


class IntimateImport(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(IntimateImport, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        _job_id = str(uuid.uuid4())
        _params = {
            "TendrlContext.integration_id": integration_id
        }
        _job_payload = {
            "tags": ["tendrl/integration/monitoring"],
            "run": "monitoring.flows.NewClusterDashboard",
            "status": "new",
            "parameters": _params,
            "parent": self.parameters['job_id'],
            "type": "monitoring"
        }
        Job(
            job_id=_job_id,
            status="new",
            payload=_job_payload
        ).save()
        logger.log(
            "debug",
            NS.publisher_id,
            {
                'message': "Job (job_id: %s) created to "
                "intimate grafana dashboard of new cluster" %
                _job_id
            }
        )
        return True
