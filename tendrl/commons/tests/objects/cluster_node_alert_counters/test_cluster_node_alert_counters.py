import __builtin__
import maps
from tendrl.commons.objects import cluster_node_alert_counters


def test_ClusterNodeAlertCounters():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict(integration_id="",
                                       cluster_name="test_name",
                                       sds_name="Test_sds")
    test = cluster_node_alert_counters.ClusterNodeAlertCounters(0, 1, None)
    test.render()
