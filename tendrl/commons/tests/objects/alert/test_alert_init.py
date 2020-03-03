import builtins
import maps
from mock import patch

from tendrl.commons import objects
from tendrl.commons.objects.alert import Alert
from tendrl.commons.objects.alert import AlertUtils


def test_alert_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "Test_id"
    with patch.object(objects.BaseObject, 'load_definition',
                      return_value=maps.NamedDict()):
        alert_obj = Alert()
        alert_obj.render()
        # Makes test not partial
        alert_obj.tags = "Test string"
        alert_obj.render()


def test_equals():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "Test_id"
    with patch.object(objects.BaseObject, 'load_definition',
                      return_value=maps.NamedDict()):
        alert1 = Alert()
        alert2 = Alert("Test 2")
        alert_ex = AlertUtils()
        alert_ex.equals(alert1, alert2)


def test_update():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "Test_id"
    with patch.object(objects.BaseObject, 'load_definition',
                      return_value=maps.NamedDict()):
        alert1 = Alert()
        alert1.severity = "INFO"
        alert2 = Alert("Test 2")
        alert2.severity = "WARNING"
        alert_ex = AlertUtils()
        alert_ex.update(alert1, alert2)
        alert1.severity = "CRITICAL"
        # Makes first if statement false
        alert_ex.update(alert1, alert2)


def test_is_same():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "Test_id"
    with patch.object(objects.BaseObject, 'load_definition',
                      return_value=maps.NamedDict()):
        alert1 = Alert()
        alert2 = Alert("Test 2")
        alert1.resource = "Test Resource1"
        alert2.resource = "Test Resource2"
        alert_ex = AlertUtils()
        # Covers first false statement where resources are different
        assert alert_ex.is_same(alert1, alert2) is False
        alert2.resource = "Test Resource1"
        alert1.tags = {"No plug": "Hi"}
        alert1.classification = ["node"]
        alert1.node_id = "node1"
        alert2.classification = ["node"]
        alert2.node_id = "node2"
        # Makes second if false, not plugin in alert1
        assert alert_ex.is_same(alert1, alert2) is False
        alert1.tags = {'plugin_instance': "Hi"}
        alert2.tags = {'plugin': "Ho"}
        # Covers if plugin is in alert1 but not alert2
        assert alert_ex.is_same(alert1, alert2) is False
        alert2.tags = {'plugin_instance': "Ho"}
        # Covers if both have the plugin_instance but their data is different
        assert alert_ex.is_same(alert1, alert2) is False
        alert2.tags = {'plugin_instance': "Hi",
                       'integration_id': 2}
        alert1.tags = {'plugin_instance': "Hi",
                       'integration_id': 1}
        # Covers if they both have the same plugin_instance
        # but different int ids
        assert alert_ex.is_same(alert1, alert2) is False
        alert2.tags = {'plugin_instance': "Hi"}
        # Alert2 now doesn't have an int id
        assert alert_ex.is_same(alert1, alert2) is False
        alert1.tags = {'plugin_instance': "Hi"}
        alert2.tags = {'plugin_instance': "Hi",
                       'integration_id': 2}
        # Now alert2 has an int id but alert1 does not
        assert alert_ex.is_same(alert1, alert2) is False
        alert1.tags = {'plugin_instance': "Hi",
                       'integration_id': 2}
        alert1.classification = ["node"]
        alert1.node_id = "node1"
        alert2.classification = ["node"]
        alert2.node_id = "node2"
        # Node in both classifications but different ids
        assert alert_ex.is_same(alert1, alert2) is False
        alert2.classification = ["no_longer_the_same"]
        # alert1 clas has node, but alert2 does not
        assert alert_ex.is_same(alert1, alert2) is False
        alert1.classification = ["no_longer_the_same"]
        alert2.classification = ["fail"]
        # Alert1 clas does not have node, and neither does Alert2
        assert alert_ex.is_same(alert1, alert2) is False
        alert2.classification = ["node"]
        # Alert1 clas does not have node, but alert2 does
        assert alert_ex.is_same(alert1, alert2) is False
        alert1.classification = ["node"]
        alert1.node_id = "node"
        alert2.classification = ["node"]
        alert2.node_id = "node"
        alert1.alert_type = "Type1"
        alert2.alert_type = "Type2"
        # Alert types are not equal
        assert alert_ex.is_same(alert1, alert2) is False
        alert2.alert_type = "Type1"
        alert2.classification = ["node", "extra"]
        # The sets are not equal due to adding an extra element to alert2
        assert alert_ex.is_same(alert1, alert2) is False
        alert2.classification.remove("extra")
        assert alert_ex.is_same(alert1, alert2) is True


def test_to_obj():
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "Test_id"
    with patch.object(objects.BaseObject, 'load_definition',
                      return_value=maps.NamedDict()):

        alert_json = {"alert_id": "Test_id",
                      "node_id": "Test_id",
                      "time_stamp": "Test_time",
                      "resource": "Test_resource",
                      "current_value": "Test_value",
                      "tags": {},
                      "alert_type": "Test_type",
                      "severity": "INFO",
                      "classification": "Test_clas",
                      "significance": "Test_sig",
                      "ackedby": "Test_ackedby",
                      "acked": "Test_acked",
                      "ack_comment": [],
                      "acked_at": "Test_acked_at",
                      "pid": 0,
                      "source": "Test_source",
                      "delivered": "Test_delivered"
                      }
        alert_ex = AlertUtils()
        alert_ex.to_obj(alert_json)
