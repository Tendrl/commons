from tendrl.commons.objects import BaseAtom
from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils.service_status import ServiceStatus


class CheckServiceStatus(BaseAtom):

    def run(self):
        service_name = self.parameters.get("Service.name")
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Checking status of %s on %s" % (
                service_name,
                NS.node_context.fqdn)},
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id']
        )
        response = ServiceStatus(service_name).status()
        # and then check the response...
        if response:
            logger.log(
                "info",
                NS.publisher_id,
                {"message": "%s running on %s" % (
                    service_name,
                    NS.node_context.fqdn)},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return True
        else:
            logger.log(
                "error",
                NS.publisher_id,
                {"message": "Failed to check status of %s on "
                 "%s" % (
                     service_name,
                     NS.node_context.fqdn)},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return False
