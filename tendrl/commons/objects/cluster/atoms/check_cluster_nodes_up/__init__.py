import etcd
import json

from tendrl.commons.objects import BaseAtom
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class CheckClusterNodesUp(BaseAtom):
    def __init__(self, *args, **kwargs):
        super(CheckClusterNodesUp, self).__init__(*args, **kwargs)

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
                logger.log(
                    "info",
                    NS.publisher_id,
                    {"message": "Checking status of nodes %s" % str(node_ids)},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                nodes_up = []
                nodes_down = []
                for node in node_ids:
                    node = str(node)
                    # if node_context not found it will give status DOWN
                    node_context = NS.tendrl.objects.NodeContext(
                        node_id=node,
                        status='DOWN'
                    ).load()
                    if node_context.status == "UP":
                        nodes_up.append(node)
                    else:
                        all_node_status_up = False
                        nodes_down.append(node)
                if all_node_status_up:
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {"message": "Nodes %s are up" % nodes_up},
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
                else:
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {"message": "Nodes %s are down" %
                         nodes_down},
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
            # no need to check for child job
            return all_node_status_up
        except (etcd.EtcdKeyNotFound, TypeError) as ex:
            logger.log(
                "error",
                NS.get("publisher_id", None),
                {
                    "message": "Error checking status of nodes. Error: %s"
                               % str(ex)
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return False
