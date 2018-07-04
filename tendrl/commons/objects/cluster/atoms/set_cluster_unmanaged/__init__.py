import etcd

from tendrl.commons import objects
from tendrl.commons.utils import log_utils as logger


class SetClusterUnmanaged(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(SetClusterUnmanaged, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        logger.log(
            "info",
            NS.get("publisher_id", None),
            {
                "message": "Setting cluster %s is_managed to \"no\":" %
                           integration_id
            },
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id']
        )
        try:
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=integration_id
            ).load()
            _cluster.is_managed = "no"
            _cluster.save()
        except etcd.EtcdKeyNotFound:
            logger.log(
                "error",
                NS.get("publisher_id", None),
                {
                    "message": "Error setting cluster %s"
                    "is_managed  to \"no\":" % (
                        integration_id
                    )
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return False

        return True
