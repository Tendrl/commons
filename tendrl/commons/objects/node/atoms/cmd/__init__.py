from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects import BaseAtom
from tendrl.commons.utils.cmd_utils import Command
from tendrl.commons.utils import log_utils as logger


class Cmd(BaseAtom):

    def run(self):
        cmd = self.parameters.get("Node.cmd_str")
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Executing %s on node %s" % (
                cmd,
                self.parameters.get("fqdn"))},
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id']
        )
        _, err, rc = Command(cmd).run()
        if not err and rc == 0:
            logger.log(
                "info",
                NS.publisher_id,
                {"message": "Successfully executed %s on node %s" % (
                    cmd,
                    self.parameters.get("fqdn"))},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return True
        else:
            logger.log(
                "error",
                NS.publisher_id,
                {"message": "Failed to execute %s on node %s."
                 "Error %s" % (
                     cmd,
                     self.parameters.get("fqdn"),
                     err)},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            raise AtomExecutionFailedError(err)
