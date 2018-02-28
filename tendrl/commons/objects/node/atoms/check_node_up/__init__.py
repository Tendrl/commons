import etcd
import json

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects import BaseAtom
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class CheckNodeUp(BaseAtom):
    def __init__(self, *args, **kwargs):
        super(CheckNodeUp, self).__init__(*args, **kwargs)

    def run(self):
        try:
            all_node_status_up = True
            # check job is parent or child
            job = NS.tendrl.objects.Job(
                job_id=self.parameters['job_id']
            ).load()
            if "parent" not in job.payload:
                # fetch node id using integration_id
                integration_id = self.parameters[
                    'TendrlContext.integration_id'
                ]
                key = "indexes/tags/tendrl/integration/%s" % \
                    integration_id
                node_ids_str = etcd_utils.read(key).value
                node_ids = json.loads(node_ids_str)
                # identifying node status using node_id
                hosts = {}
                for node in node_ids:
                    try:
                        key = "nodes/%s/NodeContext/status" % node
                        status = etcd_utils.read(key).value
                    except etcd.EtcdKeyNotFound:
                        status = None
                    hosts[str(node)] = status
                logger.log(
                    "info",
                    NS.publisher_id,
                    {"message": "Checking if nodes %s are up" % hosts.keys()},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                nodes_up = []
                nodes_down = []
                for host in hosts:
                    if hosts[host] == "UP":
                        nodes_up.append(host)
                    else:
                        all_node_status_up = False
                        nodes_down.append(host)
                if all_node_status_up:
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {"message": "Status of nodes %s are up" % nodes_up},
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
                else:
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {"message": "Status of nodes %s are down" %
                         nodes_down},
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
            # no need to check for child job
            return all_node_status_up
        except (etcd.EtcdKeyNotFound, KeyError, TypeError) as ex:
            raise FlowExecutionFailedError(
                "Error checking status of nodes .error: %s" % str(ex)
            )
