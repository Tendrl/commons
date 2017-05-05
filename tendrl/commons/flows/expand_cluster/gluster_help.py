from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.flows.exceptions import FlowExecutionFailedError


def get_node_ips(parameters):
    node_ips = []
    for node, config in parameters["Cluster.node_configuration"].iteritems():
        node_ips.append(config["provisioning_ip"])
    return node_ips


def expand_gluster(parameters):
    node_ips = get_node_ips(parameters)
    plugin = NS.gluster_provisioner.get_plugin()

    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Setting up gluster nodes %s" %
                                parameters['TendrlContext.integration_id']
                     }
        )
    )

    ret_val = plugin.setup_gluster_node(
        node_ips,
        repo=NS.config.data['glusterfs_repo']
    )
    if ret_val is not True:
        raise FlowExecutionFailedError("Error setting up gluster node")

    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={
                "message": "Expanding gluster cluster %s" %
                parameters['TendrlContext.integration_id']
            }
        )
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

    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={
                "message": "Expanded Gluster Cluster %s."
                " New nodes are: %s" % (
                    parameters['TendrlContext.integration_id'],
                    ",".join(node_ips)
                )
            }
        )
    )
