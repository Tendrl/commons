from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons import objects


class ValidCreateClusterParams(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(ValidCreateClusterParams, self).__init__(*args, **kwargs)

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

        supported_sds = NS.compiled_definitions.get_parsed_defs()[
            'namespace.tendrl'
        ]['supported_sds']
        sds_name = NS.tendrl_context.sds_name
        if sds_name not in supported_sds:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "SDS (%s) not supported" % sds_name
                    },
                    job_id=self.job_id,
                    flow_id=self.parameters['flow_id'],
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False

        # Check if cluster name contains space char and fail if so
        if ' ' in NS.tendrl_context.cluster_name:
            Event(
                Message(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Space char not allowed in cluster name"
                    },
                    job_id=self.job_id,
                    flow_id=self.parameters['flow_id'],
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            return False

        return True
