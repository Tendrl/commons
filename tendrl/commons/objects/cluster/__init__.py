from tendrl.commons import objects


class Cluster(objects.BaseObject):
    def __init__(self, integration_id=None, public_network=None,
                 cluster_network=None, node_configuration=None,
                 conf_overrides=None, node_identifier=None,
                 *args, **kwargs):
        super(Cluster, self).__init__(*args, **kwargs)
        self.integration_id=integration_id
        self.public_network = public_network
        self.cluster_network = cluster_network
        self.node_configuration = node_configuration
        self.conf_overrides = conf_overrides
        self.node_identifier = node_identifier
        self.value = 'clusters/{0}'

    def render(self):
        self.value = self.value.format(
            self.integration_id or NS.tendrl_context.integration_id
        )
        return super(Cluster, self).render()
