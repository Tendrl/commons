from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.flows.exceptions import FlowExecutionFailedError


def get_node_ips(parameters):
    node_ips = []
    for node, config in parameters["Cluster.node_configuration"].iteritems():
        node_ips.append(config["provisioning_ip"])
    return node_ips


def create_gluster(parameters):
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
            payload={"message": "Creating gluster cluster %s" %
                                parameters['TendrlContext.integration_id']
                     }
        )
    )
    ret_val = plugin.create_gluster_cluster(node_ips)
    if ret_val is not True:
        raise FlowExecutionFailedError("Error creating gluster cluster")

    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Created Gluster Cluster %s" %
                                parameters['TendrlContext.integration_id']
                     }
        )
    )
