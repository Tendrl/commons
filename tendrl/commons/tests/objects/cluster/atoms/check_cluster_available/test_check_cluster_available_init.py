import etcd
import maps
from tendrl.commons.objects.cluster.atoms.check_cluster_available import CheckClusterAvailable  # noqa
from tendrl.commons.objects.cluster import Cluster


def test_check_cluster_available():
    NS._int = maps.NamedDict
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.Cluster = Cluster()
    test = CheckClusterAvailable()
    test.parameters = maps.NamedDict()
    test.parameters['TendrlContext.integration_id'] = \
        "7a3f2238-ef79-4943-9edf-762a80cf22a0"
    NS._int.client = etcd.Client()
    test.run()
