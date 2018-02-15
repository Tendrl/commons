from tendrl.commons import objects
from tendrl.commons.utils import log_utils as logger


class ValidImportClusterParams(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(ValidImportClusterParams, self).__init__(*args, **kwargs)

    def run(self):
        if self.parameters['TendrlContext.integration_id'] is None:
            logger.log(
                "error",
                NS.publisher_id,
                {"message": "Cluster uuid (integration_id) is empty"},
                job_id=self.job_id,
                flow_id=self.parameters['flow_id'],
                integration_id=NS.tendrl_context.integration_id,
            )
            return False

        return True
