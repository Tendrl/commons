
from tendrl.commons import objects


class TendrlContext(objects.BaseObject):
    def __init__(
        self,
        integration_id=None,
        cluster_id=None,
        cluster_name=None,
        sds_name=None,
        sds_version=None,
            *args, **kwargs):
        super(TendrlContext, self).__init__(*args, **kwargs)
        # integration_id is the Tendrl generated cluster UUID
        self.integration_id = integration_id
        self.cluster_id=cluster_id
        self.cluster_name=cluster_name
        self.sds_name=sds_name
        self.sds_version=sds_version
        self.value = 'nodes/{0}/TendrlContext'

    def render(self):
        self.value = self.value.format(NS.node_context.node_id)
        return super(TendrlContext, self).render()
