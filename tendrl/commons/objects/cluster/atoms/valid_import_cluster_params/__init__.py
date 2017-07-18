from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons import objects


class ValidImportClusterParams(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(ValidImportClusterParams, self).__init__(*args, **kwargs)

    def run(self):
        if self.parameters['TendrlContext.integration_id'] is None:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Cluster uuid (integration_id) is empty"
                    },
                    job_id=self.job_id,
                    flow_id=self.parameters['flow_id'],
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False

        return True
