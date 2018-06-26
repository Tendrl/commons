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
            logger.log(
                "info",
                NS.publisher_id,
                {
                    "message": "Stopping service %s on node %s" %
                               (service, NS.node_context.node_id)
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
            )
            srv = NS.tendrl.objects.Service(service=service)
            if not srv.running:
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {
                        "message": "%s not running on "
                        "%s" % (service, NS.node_context.node_id)
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
                continue

            _cmd_str = "systemctl stop %s" % service
            cmd = cmd_utils.Command(_cmd_str)
            err, out, rc = cmd.run()
            if err:
                logger.log(
                    "error",
                    NS.publisher_id,
                    {
                        "message": "Could not stop %s"
                        " service on %s. Error: %s" % (service, err,
                                                       NS.node_context.node_id)
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
                        " service on %s. Error: %s" % (service, err,
                                                       NS.node_context.node_id)
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
                return False

        return True
