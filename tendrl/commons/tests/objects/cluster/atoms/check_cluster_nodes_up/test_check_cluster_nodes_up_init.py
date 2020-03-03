import builtins
import maps
from mock import patch

from tendrl.commons.objects.cluster.atoms.check_cluster_nodes_up import \
    CheckClusterNodesUp
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class MockJob(object):
    def __init__(self, job_id=None):
        pass

    def load(self):
        self.payload = {}
        return self


class MockNodeContext(object):
    def __init__(self, node_id=None, status=None):
        pass

    def load(self):
        self.status = 'UP'
        return self


def read(key):
    out = maps.NamedDict(
        value='["fe80532d-95e0-4b10-b486-a357e325cccf"]'
    )
    return out


# Testing run
@patch.object(logger, "log")
def test_run(log):
    log.return_value = True
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS["tendrl"] = maps.NamedDict()
    NS.tendrl["objects"] = maps.NamedDict(
        Job=MockJob,
        NodeContext=MockNodeContext
    )
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    check_cluster_nodes_up = CheckClusterNodesUp()
    check_cluster_nodes_up.parameters = maps.NamedDict()
    check_cluster_nodes_up.parameters['TendrlContext.integration_id'] = \
        "7a3f2238-ef79-4943-9edf-762a80cf22a0"
    check_cluster_nodes_up.parameters['job_id'] = "node_job"
    check_cluster_nodes_up.parameters['flow_id'] = "flow_id"
    with patch.object(etcd_utils, "read", read):
        check_cluster_nodes_up.run()
