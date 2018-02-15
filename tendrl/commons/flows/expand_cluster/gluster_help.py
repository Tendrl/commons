from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils import log_utils as logger


def get_node_ips(parameters):
    node_ips = []
    for node, config in parameters["Cluster.node_configuration"].iteritems():
        node_ips.append(config["provisioning_ip"])
    return node_ips


def expand_gluster(parameters):
    node_ips = get_node_ips(parameters)
    plugin = NS.gluster_provisioner.get_plugin()
    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Setting up gluster nodes %s" %
                    parameters['TendrlContext.integration_id']},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id'],
    )

    ret_val = plugin.setup_gluster_node(
        node_ips,
        repo=NS.config.data.get('glusterfs_repo', None)
    )
    if ret_val is not True:
        raise FlowExecutionFailedError("Error setting up gluster node")
    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Expanding gluster cluster %s" %
         parameters['TendrlContext.integration_id']},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
    )
    failed_nodes = []
    for node in node_ips:
        ret_val = plugin.expand_gluster_cluster(node)
        if not ret_val:
            failed_nodes.append(node)

    if failed_nodes:
        raise FlowExecutionFailedError(
            "Error expanding gluster cluster. Following nodes failed: %s" %
            ",".join(failed_nodes)
        )
    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Expanded Gluster Cluster %s."
         " New nodes are: %s" % (
             parameters['TendrlContext.integration_id'],
             ",".join(node_ips))},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
    )
