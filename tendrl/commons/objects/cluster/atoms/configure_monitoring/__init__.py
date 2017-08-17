import json
import subprocess


from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils.service import Service


NODE_PLUGINS = {
    'collectd',
    'cpu',
    'mount_point',
    'memory',
    'swap',
    'network',
    'latency',
    'disk',
    'dbpush'
}


GLUSTER_CLUSTER_PLUGINS = {
    'tendrl_glusterfs_brick_utilization',
    'tendrl_glusterfs_health_counters',
    'tendrl_glusterfs_peer_network_throughput',
    'tendrl_glusterfs_profile_info'
}


class ConfigureMonitoring(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(ConfigureMonitoring, self).__init__(*args, **kwargs)

    def _configure_plugin(self, plugin_name, plugin_params):
        logger.log(
            "info",
            NS.get("publisher_id", None),
            {
                "message": "Starting configuration of %s on %s with %s"
                "as conf parameters" % (
                    plugin_name,
                    NS.node_context.fqdn,
                    json.dumps(plugin_params).encode('utf-8')
                )
            },
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id']
        )
        try:
            subprocess.check_call(
                [
                    "tendrl-monitoring-config-manager",
                    plugin_name,
                    json.dumps(plugin_params)
                ]
            )
            return True
        except subprocess.CalledProcessError as ex:
            logger.log(
                "error",
                NS.get("publisher_id", None),
                {
                    "message": "Error configuring %s on %s with %s"
                    "as conf parameters. Error %s" % (
                        plugin_name,
                        NS.node_context.fqdn,
                        json.dumps(plugin_params).encode('utf-8'),
                        str(ex)
                    )
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return False

    def run(self):
        self.parameters['Service.name'] = 'collectd'
        plugin_config_success = True
        graphite_host = (
            NS.config.data.get('graphite_host') or
            NS.config.data['etcd_connection']
        )
        graphite_port = (
            NS.config.data.get('graphite_port') or
            2003
        )
        plugin_params = {
            "graphite_host": graphite_host,
            "graphite_port": graphite_port,
            "hostname": NS.node_context.fqdn,
            "integration_id": NS.tendrl_context.integration_id,
            "node_id": NS.node_context.node_id,
            "logging_socket_path": NS.config.data['logging_socket_path']
        }
        for node_plugin in NODE_PLUGINS:
            plugin_config_success &= self._configure_plugin(
                node_plugin,
                plugin_params
            )
        if NS.tendrl_context.sds_name == 'gluster':
            for gluster_plugin in GLUSTER_CLUSTER_PLUGINS:
                plugin_config_success &= self._configure_plugin(
                    gluster_plugin,
                    plugin_params
                )
        if not plugin_config_success:
            raise AtomExecutionFailedError(
                "Collectd configuration failed for node %s from cluster %s" % (
                    NS.node_context.fqdn,
                    NS.tendrl_context.integration_id
                )
            )
        err, success = Service(
            'collectd',
            publisher_id='node_agent',
            node_id=NS.node_context.node_id,
            socket_path=NS.config.data['logging_socket_path'],
            enabled=True
        ).restart()

        return True
