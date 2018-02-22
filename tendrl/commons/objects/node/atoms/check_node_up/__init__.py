import etcd
import json

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects import BaseAtom
from tendrl.commons.utils.cmd_utils import Command
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class CheckNodeUp(BaseAtom):
    def __init__(self, *args, **kwargs):
        super(CheckNodeUp, self).__init__(*args, **kwargs)

    def run(self):
        try:
            flag = True
            # check job is parent or child
            job = NS.tendrl.objects.Job(
                job_id=self.parameters['job_id']
            ).load()
            if "parent" not in job.payload:
                # Getting node_ids from parameters
                node_ids = self.parameters.get(
                    'Node[]',
                    None
                )
                if not node_ids:
                    # fetch node id using integration_id
                    integration_id = self.parameters[
                        'TendrlContext.integration_id'
                    ]
                    key = "indexes/tags/tendrl/integration/%s" % \
                        integration_id
                    node_ids_str = etcd_utils.read(key).value
                    node_ids = json.loads(node_ids_str)
                # identifying fqdn using node_id
                hosts = []
                for node in node_ids:
                    key = "nodes/%s/NodeContext/fqdn" % node
                    fqdn = etcd_utils.read(key).value
                    hosts.append(str(fqdn))
                logger.log(
                    "info",
                    NS.publisher_id,
                    {"message": "Checking if nodes %s are up" % hosts},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                nodes_up = []
                nodes_down = []
                for fqdn in hosts:
                    out, err, rc = Command("ping -c 1 %s" % fqdn).run()
                    # and then check the response...
                    if not err and rc == 0:
                        nodes_up.append(fqdn)
                    else:
                        flag = False
                        nodes_down.append(fqdn)
                if flag:
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {"message": "Ping to nodes %s succeeded." % nodes_up},
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
                else:
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {"message": "Failed to ping nodes %s" % nodes_down},
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
            # no need to check for child job
            return flag
        except (etcd.EtcdKeyNotFound, KeyError, TypeError) as ex:
            raise FlowExecutionFailedError(
                "Error checking status of nodes .error: %s" % str(ex)
            )
