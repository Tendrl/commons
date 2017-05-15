
from tendrl.commons import objects


class DetectedCluster(objects.BaseObject):
    def __init__(self, detected_cluster_id=None, detected_cluster_name=None,
                 sds_pkg_name=None, sds_pkg_version=None, *args, **kwargs):
        super(DetectedCluster, self).__init__(*args, **kwargs)

        self.value = 'nodes/{0}/DetectedCluster'
        self.detected_cluster_id = detected_cluster_id
        self.detected_cluster_name = detected_cluster_name
        self.sds_pkg_name = sds_pkg_name
        self.sds_pkg_version = sds_pkg_version

    def render(self):
        self.value = self.value.format(NS.node_context.node_id)
        return super(DetectedCluster, self).render()
