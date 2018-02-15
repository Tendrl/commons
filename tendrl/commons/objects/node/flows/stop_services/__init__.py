from tendrl.commons import flows
from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils import log_utils as logger


class StopServices(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(StopServices, self).__init__(*args, **kwargs)

    def run(self):
        super(StopServices, self).run()
        services = self.parameters['Services[]']
        for service in services:
            _cmd_str = "systemctl stop %s" % service
            cmd = cmd_utils.Command(_cmd_str)
            err, out, rc = cmd.run()
            if err:
                logger.log(
                    "error",
                    NS.publisher_id,
                    {
                        "message": "Could not stop %s"
                        " service. Error: %s" % (service, err)
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
                return False

            _cmd_str = "systemctl disable %s" % service
            cmd = cmd_utils.Command(_cmd_str)
            err, out, rc = cmd.run()
            if err:
                logger.log(
                    "error",
                    NS.publisher_id,
                    {
                        "message": "Could not disable %s"
                        " service. Error: %s" % (service, err)
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
                return False

        return True
