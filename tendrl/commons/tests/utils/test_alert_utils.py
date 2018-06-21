import __builtin__
import maps

from tendrl.commons.utils.alert_utils import alert_job_status as tendrl_alert

_test_curr_value = "failed"
_test_message = "TEST"

def test_alert_job_status_fail():
   setattr(__builtin__, "NS", maps.NamedDict())
   NS.publisher_id = 2
   NS.tendrl_context = maps.NamedDict(integration_id="", cluster_name="test_name", sds_name="Test_sds")
   NS.node_context = maps.NamedDict(fqdn="test", node_id="test_node_id")
   tendrl_alert(_test_curr_value, _test_message)


def test_alert_job_status_early_return():
   setattr(__builtin__, "NS", maps.NamedDict())
   NS.publisher_id = 2
   NS.tendrl_context = maps.NamedDict(integration_id="", cluster_name="test_name", sds_name="Test_sds")
   NS.node_context = maps.NamedDict(fqdn="test", node_id="")
   tendrl_alert(_test_curr_value, _test_message)
