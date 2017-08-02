from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.utils.cmd_utils import Command
from tendrl.commons.utils import log_utils as logger


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
                    plugin_params
                )
            },
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id']
        )
        cmd_str = "tendrl_monitoring_config_manager %s '%s'" % (
            plugin_name,
            plugin_params
        )
        out, err, rc = Command(cmd_str).run()
        if not err and rc == 0:
            logger.log(
                "info",
                NS.get("publisher_id", None),
                {
                    "message": "Configured %s on %s with %s"
                    "as conf parameters" % (
                        plugin_name,
                        NS.node_context.fqdn,
                        plugin_params
                    )
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return True
        else:
            logger.log(
                "error",
                NS.get("publisher_id", None),
                {
                    "message": "Configuring %s on %s with %s"
                    "as conf parameters failed.Error %s."
                    "Return code %s" % (
                        plugin_name,
                        NS.node_context.fqdn,
                        plugin_params,
                        err,
                        rc
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
            'graphite_host': graphite_host,
            'graphite_port': graphite_port,
            'hostname': NS.node_context.fqdn,
            'integration_id': NS.tendrl_context.integration_id,
            'node_id': NS.node_context.node_id,
            'logging_socket_path': NS.config.data['logging_socket_path']
        }
        for node_plugin in NODE_PLUGINS:
            plugin_config_success &= self._configure_plugin(
                node_plugin,
                plugin_params
            )
        plugin_config_success &= self._configure_plugin(
            'tendrl_%s' % NS.tendrl_context.sds_name,
            plugin_params
        )
        if not plugin_config_success:
            raise AtomExecutionFailedError(
                "Collectd configuration failed for node %s from cluster %s" % (
                    NS.node_context.fqdn,
                    NS.tendrl_context.integration_id
                )
            )
