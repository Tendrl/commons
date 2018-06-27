from tendrl.commons.objects.alert import Alert
from tendrl.commons.objects.alert import AlertUtils


def test_alert_render():
    alert_obj = Alert()
    alert_obj.render()


def test_alert_utils_equals():

    alert_utils_obj = AlertUtils()

    # should succeed - objects are identical
    alert_obj_1 = Alert(
        alert_id="test_alert_id",
        acked="test_acked",
        severity='INFO'
    )
    alert_obj_2 = Alert(
        alert_id="test_alert_id",
        acked="test_acked",
        severity='INFO'
    )
    assert alert_utils_obj.equals(alert_obj_1, alert_obj_2) == True

    # should fail - objects are different
    alert_obj_1 = Alert(
        alert_id="test_alert_id_unique",
        acked="test_acked",
        severity='INFO'
    )
    alert_obj_2 = Alert(
        alert_id="test_alert_id_also_unique",
        acked="test_acked",
        severity='INFO'
    )
    assert alert_utils_obj.equals(alert_obj_1, alert_obj_2) == False


def test_alert_utils_update():

    alert_utils_obj = AlertUtils()

    new_alert_obj = Alert(
        alert_id="new_alert_id",
        severity='INFO'
    )
    exisiting_alert_obj = Alert(
        alert_id="existing_alert_id",
        severity='INFO'
    )

    alert_utils_obj.update(new_alert_obj, exisiting_alert_obj)
    assert new_alert_obj.alert_id == "existing_alert_id"


def test_alert_utils_is_same():

    alert_utils_obj = AlertUtils()

    # alert1.resource != alert2.resource branch
    alert_obj_1 = Alert(
        resource="test_resource_1"
    )
    alert_obj_2 = Alert(
        resource="test_resource_2"
    )
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False

    # plugin_instance in one object but not the other
    alert_obj_1 = Alert(
        tags={'plugin_instance': "test_1"}
    )
    alert_obj_2 = Alert()
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False

    # plugin_instance in both but different
    alert_obj_2 = Alert(
        tags={'plugin_instance': "test_2"}
    )
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False

    # integration_id in one object but not the other
    alert_obj_1 = Alert(
        tags={'integration_id': "test_1"}
    )
    alert_obj_2 = Alert()
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False
    assert alert_utils_obj.is_same(alert_obj_2, alert_obj_1) == False

    # integration_id in both but different
    alert_obj_2 = Alert(
        tags={'integration_id': "test_2"}
    )
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False

    # 'node' in both but different
    alert_obj_1 = Alert(
        node_id="test_node_id_1",
        classification="node"
    )
    alert_obj_2 = Alert(
        node_id="test_node_id_2",
        classification="node"
    )
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False

    # 'node' in one object but not the other
    alert_obj_2 = Alert(
        node_id="test_id",
        classification="test_classification"
    )
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False
    assert alert_utils_obj.is_same(alert_obj_2, alert_obj_1) == False

    # different alert types
    alert_obj_1 = Alert(
        node_id="test_id",
        classification="test_classification",
        alert_type='test_type_1'
    )
    alert_obj_2 = Alert(
        node_id="test_id",
        classification="test_classification",
        alert_type='test_type_2'
    )
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False

    # different classifications
    alert_obj_1 = Alert(
        node_id="test_id",
        classification='test_classification_1'
    )
    alert_obj_2 = Alert(
        node_id="test_id",
        classification='test_classification_2'
    )
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == False

    # success case
    alert_obj_1 = Alert(
        node_id="test_id",
        classification="test_classification"
    )
    alert_obj_2 = Alert(
        node_id="test_id",
        classification="test_classification"
    )
    assert alert_utils_obj.is_same(alert_obj_1, alert_obj_2) == True


def test_alert_utils_to_obj():
    alert_utils_obj = AlertUtils()
    alert_json = {
        'alert_id': 'test_alert_id',
        'node_id': 'test_node_id',
        'time_stamp': '12:00',
        'resource': 'test_resource',
        'current_value': 'test_current_value',
        'tags': {'test_tag_key': 'test_tag_value'},
        'alert_type': 'test_alert_type',
        'severity': 'INFO',
        'pid': 1,
        'source': 'test_source'
    }
    alert_utils_obj.to_obj(alert_json)
