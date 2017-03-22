from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.objects import BaseAtom
from tendrl.commons.utils.service_status import ServiceStatus


class CheckServiceStatus(BaseAtom):

    def run(self):
        service_name = self.parameters.get("Service.name")
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Checking status of service %s on node %s" % (
                        service_name,
                        self.parameters.get("fqdn")
                    )
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
            )
        )
        response = ServiceStatus("systemctl status %s" % service_name).status()
        # and then check the response...
        if response:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Service %s running on node %s" % (
                            service_name,
                            self.parameters.get("fqdn")
                        )
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
            )
            return True
        else:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Failed to check status of service %s on "
                        "node %s" % (
                            service_name,
                            self.parameters.get("fqdn")
                        )
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
            )
            return False
