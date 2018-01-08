import etcd

from tendrl.commons import objects
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class SetClusterUnmanaged(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(SetClusterUnmanaged, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']

        try:
            etcd_utils.write(
                "/clusters/%s/is_managed" % integration_id,
                "no"
            )
        except etcd.EtcdKeyNotFound:
            logger.log(
                "error",
                NS.get("publisher_id", None),
                {
                    "message": "Error setting cluster"
                    "is_managed \"no\": (%s)" % (
                        integration_id
                    )
                },
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            return False

        return True
