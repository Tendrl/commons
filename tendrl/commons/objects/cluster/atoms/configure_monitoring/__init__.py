import json
import netifaces
import socket
import subprocess


from tendrl.commons import objects
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
    'tendrl_gluster',
    'tendrl_gluster_brick_disk_stats'
}


class ConfigureMonitoring(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(ConfigureMonitoring, self).__init__(*args, **kwargs)

    def _configure_plugin(self, plugin_name, plugin_params):
        logger.log(
            "info",
            NS.get("publisher_id", None),
            {
                "message": "Starting configuration of %s on %s "
                % (
                    plugin_name,
                    NS.node_context.fqdn
                )
            },
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id']
        )
        try:
            subprocess.check_call(
                [
                    "tendrl-monitoring-config-manager",
                    NS.node_context.fqdn,
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

    def get_node_interface(self, fqdn):
        ret_val = ''
        infs = netifaces.interfaces()
        ip = socket.gethostbyname(fqdn)
        for inf in infs:
            try:
                inf_ip = netifaces.ifaddresses(
                    inf)[netifaces.AF_INET][0]['addr']
                if inf_ip == ip:
                    return inf
            except KeyError:
                continue
        return ret_val

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
            "fqdn": NS.node_context.fqdn,
            "integration_id": NS.tendrl_context.integration_id,
            "node_id": NS.node_context.node_id,
            "logging_socket_path": NS.config.data['logging_socket_path'],
            "interval": NS.config.data['sync_interval'],
            "interface": self.get_node_interface(NS.node_context.fqdn),
            "etcd_host": NS.config.data['etcd_connection'],
            "etcd_port": NS.config.data['etcd_port']
        }
        etcd_ca_cert_file = NS.config.data.get("etcd_ca_cert_file")
        etcd_cert_file = NS.config.data.get("etcd_cert_file")
        etcd_key_file = NS.config.data.get("etcd_key_file")
        if etcd_ca_cert_file and str(etcd_ca_cert_file) != "" \
            and etcd_cert_file and str(etcd_cert_file) != "" \
            and etcd_key_file and str(etcd_key_file) != "":
            plugin_params.update({
                "etcd_ca_cert_file": NS.config.data['etcd_ca_cert_file'],
                "etcd_cert_file": NS.config.data['etcd_cert_file'],
                "etcd_key_file": NS.config.data['etcd_key_file']
            })

        for node_plugin in NODE_PLUGINS:
            plugin_config_success &= self._configure_plugin(
                node_plugin,
                plugin_params
            )
        if NS.tendrl_context.sds_name in ['gluster', 'RHGS']:
            plugin_params['is_provisioner_node'] = False
            if "provisioner/%s" % (
                NS.tendrl_context.integration_id
            ) in NS.node_context.tags:
                plugin_params['is_provisioner_node'] = True
            for gluster_plugin in GLUSTER_CLUSTER_PLUGINS:
                plugin_config_success &= self._configure_plugin(
                    gluster_plugin,
                    plugin_params
                )
        if not plugin_config_success:
            logger.log(
                "error",
                NS.get("publisher_id", None),
                {
                    "message": "Collectd configuration failed for node %s from"
                               " cluster %s" %
                               (NS.node_context.fqdn,
                                NS.tendrl_context.integration_id)
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return False
        err, success = Service(
            'collectd',
            publisher_id='node_agent',
            node_id=NS.node_context.node_id,
            enabled=True
        ).restart()
        return True
