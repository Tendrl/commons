from tendrl.commons import objects


class PersistClusterDetailsAfterCreate(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(PersistClusterDetailsAfterCreate, self).__init__(*args, **kwargs)

    def run(self):
        # Persist the cluster's extra details
        NS.tendrl.objects.Cluster(
            integration_id=self.parameters['TendrlContext.integration_id'],
            public_network=self.parameters.get('Cluster.public_network'),
            cluster_network=self.parameters.get('Cluster.cluster_network')
        ).save()

        return True
