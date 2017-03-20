from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.objects import BaseAtom
from tendrl.commons.utils.cmd_utils import Command


class CheckNodeUp(BaseAtom):

    def run(self):
        fqdn = self.parameters.get("fqdn")
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Checking if node %s is up" %
                    self.parameters.get("fqdn"),
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
            )
        )
        out, err, rc = Command("ping -c 1 %s" % fqdn).run()
        # and then check the response...
        if not err and rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Ping to %s succeeded." %
                        self.parameters.get("fqdn"),
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
                        "message": "Failed to ping %s. Error %s" % (
                            self.parameters.get("fqdn"),
                            err
                        )
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
            )
            return False
