import etcd

from tendrl.commons import objects


class IsClusterManaged(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(IsClusterManaged, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']

        try:
            cluster = NS.tendrl.objects.Cluster(
                integration_id=integration_id
            ).load()
            if cluster.is_managed.lower() == "yes":
                return True
            else:
                return False
        except etcd.EtcdKeyNotFound:
            # return true as cluster is not present only. atom should pass
            return True
