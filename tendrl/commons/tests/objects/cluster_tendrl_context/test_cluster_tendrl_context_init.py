import builtins
import maps


from tendrl.commons.objects.cluster_tendrl_context import ClusterTendrlContext


# Testing __init__
def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    setattr(builtins, "NS", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = "Test_integration_id"
    cluster_tendrl_context = ClusterTendrlContext()
    assert cluster_tendrl_context.integration_id == "Test_integration_id"
    cluster_tendrl_context = ClusterTendrlContext(
        integration_id=1,
        cluster_id=2,
        cluster_name="Test_cluster",
        sds_name="Test_sds",
        sds_version=1.1)
    assert cluster_tendrl_context.cluster_id == 2
    assert cluster_tendrl_context.cluster_name == "Test_cluster"


# Testing render
def test_render():
    setattr(builtins, "NS", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = "Test_integration_id"
    cluster_tendrl_context = ClusterTendrlContext()
    assert cluster_tendrl_context.render() is not None
