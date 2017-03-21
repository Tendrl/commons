from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects import BaseAtom
from tendrl.commons.utils.cmd_utils import Command


class Cmd(BaseAtom):

    def run(self):
        cmd = self.parameters.get("Node.cmd_str")
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Executing %s on node %s" % (
                        cmd,
                        self.parameters.get("fqdn")
                    )
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
            )
        )
        out, err, rc = Command(cmd).run()
        if not err and rc == 0:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Successfully executed %s on node %s" % (
                            cmd,
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
                        "message": "Failed to execute %s on node %s."
                        "Error %s" % (
                            cmd,
                            self.parameters.get("fqdn"),
                            err
                        )
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
            )
            raise AtomExecutionFailedError(err)
