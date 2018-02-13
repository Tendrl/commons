from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils import log_utils as logger


def get_node_ips(parameters):
    node_ips = []
    for node, config in parameters["Cluster.node_configuration"].iteritems():
        node_ips.append(config["provisioning_ip"])
    return node_ips


def create_gluster(parameters):
    node_ips = get_node_ips(parameters)
    plugin = NS.gluster_provisioner.get_plugin()

    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Setting up gluster nodes %s" %
                    parameters['TendrlContext.integration_id']},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
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
        {"message": "Creating gluster cluster %s" %
                    parameters['TendrlContext.integration_id']},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
    )
    ret_val = plugin.create_gluster_cluster(node_ips)
    if ret_val is not True:
        raise FlowExecutionFailedError("Error creating gluster cluster")

    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Created Gluster Cluster %s" %
                    parameters['TendrlContext.integration_id']},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
    )
