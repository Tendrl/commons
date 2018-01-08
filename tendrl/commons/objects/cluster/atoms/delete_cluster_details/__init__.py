import ast
import etcd

from tendrl.commons import objects
from tendrl.commons.utils import log_utils as logger


class DeleteClusterDetails(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(DeleteClusterDetails, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        cluster_tendrl_context = NS.tendrl.objects.ClusterTendrlContext(
            integration_id=integration_id
        ).load()

        etcd_keys_to_delete = []
        etcd_keys_to_delete.append(
            "/clusters/%s" % integration_id
        )
        etcd_keys_to_delete.append(
            "/alerting/clusters/%s" % integration_id
        )
        etcd_keys_to_delete.append(
            "/indexes/tags/detected_cluster/%s" %
            cluster_tendrl_context.cluster_id
        )
        etcd_keys_to_delete.append(
            "/indexes/tags/detected_cluster_id_to_integration_id/%s" %
            cluster_tendrl_context.cluster_id
        )
        etcd_keys_to_delete.append(
            "/indexes/tags/provisioner/%s" % integration_id
        )
        etcd_keys_to_delete.append(
            "/indexes/tags/tendrl/integration/%s" %
            integration_id
        )
        nodes = NS._int.client.read(
            "/clusters/%s/nodes" % integration_id
        )
        node_ids = []
        for node in nodes.leaves:
            node_id = node.key.split("/")[-1]
            node_ids.append(node_id)
            etcd_keys_to_delete.append(
                "/alerting/nodes/%s" % node_id
            )

        # Find the alerting/alerts entries to be deleted
        try:
            cluster_alert_ids = NS._int.client.read(
                "/alerting/clusters"
            )
            for entry in cluster_alert_ids.leaves:
                ca_id = entry.key.split("/")[-1]
                etcd_keys_to_delete.append(
                    "/alerting/alerts/%s" % ca_id
                )
        except etcd.EtcdKeyNotFound:
            # No cluster alerts, continue
            pass

        try:
            node_alert_ids = NS._int.client.read(
                "/alerting/nodes"
            )
            for entry in node_alert_ids.leaves:
                na_id = entry.key.split("/")[-1]
                etcd_keys_to_delete.append(
                    "/alerting/alerts/%s" % na_id
                )
        except etcd.EtcdKeyNotFound:
            # No node alerts, continue
            pass

        # Remove the cluster details
        for key in list(set(etcd_keys_to_delete)):
            try:
                NS._int.client.delete(key, recursive=True)
            except etcd.EtcdKeyNotFound:
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {
                        "message": "The key: %s not found for deletion" %
                        key
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
                continue

        # Load the gluster servers list and remove
        # the cluster nodes
        try:
            gl_srvr_list = NS._int.client.read(
                "/indexes/tags/gluster/server"
            ).value
            gl_srvr_list = ast.literal_eval(gl_srvr_list)
            for node_id in node_ids:
                if node_id in gl_srvr_list:
                    gl_srvr_list.remove(node_id)
            NS._int.client.write(
                "/indexes/tags/gluster/server",
                gl_srvr_list
            )
        except etcd.EtcdKeyNotFound:
            pass

        return True
