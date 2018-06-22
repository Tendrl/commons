import etcd
import maps
import pytest
from tendrl.commons.objects.cluster.atoms.check_cluster_available import CheckClusterAvailable  # noqa
from tendrl.commons.objects import AtomExecutionFailedError


class MockCluster(object):
    def __init__(self, integration_id = 0):
        self.is_managed = True
    def load(self):
        return self
    def exists(self):
        return self



def test_check_cluster_available():
    NS.publisher_id = 0
    NS._int = maps.NamedDict()
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.Cluster = MockCluster
    test = CheckClusterAvailable()
    test.parameters = maps.NamedDict()
    test.parameters['TendrlContext.integration_id'] = \
        "7a3f2238-ef79-4943-9edf-762a80cf22a0"
    test.parameters['job_id'] = 0
    test.parameters['flow_id'] = 0
    NS.tendrl_context = maps.NamedDict(integration_id="")
    NS._int.client = etcd.Client()
    with pytest.raises(AtomExecutionFailedError):
        test.run()
