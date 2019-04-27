import ast
import etcd

from tendrl.commons import objects
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


TENDRL_SERVICES = {
    "server": [
        "tendrl-node-agent",
        "tendrl-monitoring-integration",
        "tendrl-api",
    ],
    "storage_node": [
        "tendrl-node-agent",
        "glusterd",
    ]
}


class CheckRequiredServicesRunning(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(CheckRequiredServicesRunning, self).__init__(*args, **kwargs)

    def run(self):
        node_context = NS.tendrl.objects.NodeContext().load()
        tags = list(node_context.tags)
        required_services_running = True
        if "tendrl/monitor" in tags or \
                "tendrl/integration/monitoring" in tags:
            # check neccessary service status in server
            required_services_running = self.check_service_status(
                TENDRL_SERVICES["server"],
                "server-node"
            )
        else:
            # check neccessary service status in storage nodes
            required_services_running = self.check_service_status(
                TENDRL_SERVICES["storage_node"],
                NS.node_context.fqdn
            )
            node_list = self.parameters['Node[]']
            if required_services_running and len(node_list) > 1:
                # check monitoring integration is running on server from
                # bootstrap node only
                try:
                    node_arr = etcd_utils.read(
                        "/indexes/tags/tendrl/integration/monitoring"
                    ).value
                    node_id = ast.literal_eval(node_arr)[0]
                    service = NS.tendrl.objects.Service(
                        service="tendrl-monitoring-integration",
                        node_id=node_id
                    ).load()
                    if not service.running:
                        if len(service.error) > 0:
                            msg = ("Failed to check status of "
                                   "tendrl-monitoring-integration on "
                                   "server-node. Error: %s" % service.error)
                        else:
                            msg = ("Service tendrl-monitoring-integration is "
                                   "not running on a server-node, Please "
                                   "check the log file to figure out "
                                   "the exact problem")
                        logger.log(
                            "error",
                            NS.get("publisher_id", None),
                            {
                                "message": msg
                            },
                            job_id=self.parameters['job_id'],
                            flow_id=self.parameters['flow_id']
                        )
                        required_services_running = False
                except (etcd.EtcdKeyNotFound, IndexError):
                    msg = ("Unable to check the running status of "
                           "tendrl-monitoring-integration service"
                           )
                    logger.log(
                        "error",
                        NS.get("publisher_id", None),
                        {
                            "message": msg
                        },
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
                    required_services_running = False
        return required_services_running

    def check_service_status(self, services, node):
        required_services_running = True
        for service_name in services:
            service = NS.tendrl.objects.Service(
                service=service_name
            )
            if not service.running:
                if len(service.error) > 0:
                    msg = ("Failed to check status of %s "
                           "on %s. Error: %s" % (
                               service_name,
                               node,
                               service.error
                           ))
                else:
                    msg = ("Service %s is not running on %s, "
                           "Please check the log file to figure out the "
                           "exact problem" % (service_name, node))
                logger.log(
                    "error",
                    NS.get("publisher_id", None),
                    {
                        "message": msg
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                required_services_running = False
        return required_services_running
