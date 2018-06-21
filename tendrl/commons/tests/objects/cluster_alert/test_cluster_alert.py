import __builtin__
import maps
from tendrl.commons.objects import cluster_alert

def test_ClusterAlert():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict(integration_id="", cluster_name="test_name", sds_name="Test_sds")
    test = cluster_alert.ClusterAlert("Test Alert")
    test.render()