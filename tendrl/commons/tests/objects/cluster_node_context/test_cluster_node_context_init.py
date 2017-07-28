import __builtin__
import maps

from tendrl.commons.objects.cluster_node_context import ClusterNodeContext
from tendrl.commons.tests.fixtures.nodecontext import NodeContext


def load(*args):
    node_context = maps.NamedDict()
    node_context.machine_id = "Test machine id"
    node_context.node_id = 1
    node_context.fqdn = "Test fqdn"
    node_context.tags = ["test_tag1", "test_tag2"]
    node_context.status = True
    node_context.sync_status = True
    node_context.last_sync = "test_last_sync"
    return node_context


# Testing __init__
def test_constructor(monkeypatch):
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    setattr(__builtin__, "NS", maps.NamedDict())
    monkeypatch.setattr(NodeContext, 'load', load)
    NS.node_context = NodeContext()
    cluster_node_context = ClusterNodeContext()
    assert cluster_node_context.status
    cluster_node_context = ClusterNodeContext("Test machine id")
    assert cluster_node_context.machine_id == "Test machine id"


# Testing render
def test_render(monkeypatch):
    setattr(__builtin__, "NS", maps.NamedDict())
    monkeypatch.setattr(NodeContext, 'load', load)
    NS.node_context = NodeContext()
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = 1
    cluster_node_context = ClusterNodeContext()
    assert cluster_node_context.render() is not None
