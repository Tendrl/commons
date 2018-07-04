import etcd

from tendrl.commons import objects
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class DeleteClusterDetails(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(DeleteClusterDetails, self).__init__(*args, **kwargs)

    def run(self):
        logger.log(
            "info",
            NS.publisher_id,
            {
                "message": "Deleting cluster details."
            },
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id'],
        )
        integration_id = self.parameters['TendrlContext.integration_id']

        etcd_keys_to_delete = []
        etcd_keys_to_delete.append(
            "/clusters/%s/nodes" % integration_id
        )
        etcd_keys_to_delete.append(
            "/clusters/%s/Bricks" % integration_id
        )
        etcd_keys_to_delete.append(
            "/clusters/%s/Volumes" % integration_id
        )
        etcd_keys_to_delete.append(
            "/clusters/%s/GlobalDetails" % integration_id
        )
        etcd_keys_to_delete.append(
            "/clusters/%s/TendrlContext" % integration_id
        )
        etcd_keys_to_delete.append(
            "/clusters/%s/Utilization" % integration_id
        )
        etcd_keys_to_delete.append(
            "/clusters/%s/raw_map" % integration_id
        )
        etcd_keys_to_delete.append(
            "/alerting/clusters/%s" % integration_id
        )
        nodes = etcd_utils.read(
            "/clusters/%s/nodes" % integration_id
        )
        node_ids = []
        for node in nodes.leaves:
            node_id = node.key.split("/")[-1]
            node_ids.append(node_id)
            key = "/alerting/nodes/%s" % node_id
            etcd_keys_to_delete.append(
                key
            )
            try:
                # delete node alerts from /alerting/alerts
                node_alerts = etcd_utils.read(key)
                for node_alert in node_alerts.leaves:
                    etcd_keys_to_delete.append(
                        "/alerting/alerts/%s" % node_alert.key.split(
                            "/")[-1]
                    )
            except etcd.EtcdKeyNotFound:
                # No node alerts, continue
                pass

        # Find the alerting/alerts entries to be deleted
        try:
            cluster_alert_ids = etcd_utils.read(
                "/alerting/clusters/%s" % integration_id
            )
            for entry in cluster_alert_ids.leaves:
                ca_id = entry.key.split("/")[-1]
                etcd_keys_to_delete.append(
                    "/alerting/alerts/%s" % ca_id
                )
        except etcd.EtcdKeyNotFound:
            # No cluster alerts, continue
            pass

        # Remove the cluster details
        for key in list(set(etcd_keys_to_delete)):
            try:
                etcd_utils.delete(key, recursive=True)
            except etcd.EtcdKeyNotFound:
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {
                        "message": "%s key not found for deletion" %
                        key
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                )
                continue
        # remove short name
        cluster = NS.tendrl.objects.Cluster(
            integration_id=integration_id
        ).load()
        cluster.short_name = ""
        cluster.save()

        return True
