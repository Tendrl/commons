import logging

from tendrl.commons.flows.exceptions import FlowExecutionFailedError

LOG = logging.getLogger(__name__)


def get_node_ips(parameters):
    node_ips = []
    for node, config in parameters["node_configuration"].iteritems():
        node_ips.append(config["provisioning_ip"])
    return node_ips

def create_gluster(parameters):
    node_ips = get_node_ips(parameters)
    plugin = NS.gluster_provisioner.get_plugin()

    LOG.info("Setting up gluster nodes %s" % parameters['fsid'])
    ret_val = plugin.setup_gluster_node(node_ips)
    if ret_val is not True:
        raise FlowExecutionFailedError("Error setting up gluster node")

    LOG.info("Creating gluster cluster %s" % parameters['fsid'])
    ret_val = plugin.create_gluster_cluster(node_ips)
    if ret_val is not True:
        raise FlowExecutionFailedError("Error creating gluster cluster")

    LOG.info("Created Gluster Cluster %s" % parameters['fsid'])
