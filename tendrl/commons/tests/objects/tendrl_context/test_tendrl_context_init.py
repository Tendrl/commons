import pytest
import maps
import __builtin__
from tendrl.commons.objects.tendrl_context import TendrlContext


# Testing __init__
def test_constructor():
    '''
    Testing for constructor involves checking if all needed
    variales are declared initialized
    '''
    tendrl_context = TendrlContext()
    assert tendrl_context.integration_id is None
    
    #Passing Dummy Values
    tendrl_context = TendrlContext(
        integration_id="Test_integration_id",
        cluster_id="Test_cluster_id",
        cluster_name="Test_cluster",
        sds_name="Test_sds",
        sds_version=1.1)
    assert tendrl_context.cluster_id == "Test_cluster_id"

# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    tendrl_context = TendrlContext()
    assert tendrl_context.render() is not None
