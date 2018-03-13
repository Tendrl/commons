import json

from tendrl.commons import objects
from tendrl.commons.utils.time_utils import now

alert_severity_map = {
    'INFO': 0,
    'WARNING': 1,
    'CRITICAL': 2
}


class Alert(objects.BaseObject):
    def __init__(
        self,
        alert_id=None,
        node_id=None,
        time_stamp=None,
        resource=None,
        current_value=None,
        tags={},
        alert_type=None,
        severity=None,
        classification=None,
        significance=None,
        ackedby=None,
        acked=None,
        ack_comment=[],
        acked_at=None,
        pid=None,
        source=None,
        delivered=None,
        *args,
        **kwargs
    ):
        super(Alert, self).__init__(*args, **kwargs)
        self.alert_id = alert_id
        self.node_id = node_id
        self.time_stamp = time_stamp
        self.resource = resource
        self.current_value = current_value
        self.tags = tags
        self.alert_type = alert_type
        self.severity = severity
        self.classification = classification
        self.significance = significance
        self.ackedby = ackedby
        self.acked = acked
        self.ack_comment = ack_comment
        self.acked_at = acked_at
        self.pid = pid
        self.source = source
        self.delivered = delivered
        self.value = 'alerting/alerts/{0}'
        self.list = 'alerting/alerts'

    def render(self):
        self.value = self.value.format(self.alert_id)
        # To read tags using loads method
        if type(self.tags) != str:
            self.tags = json.dumps(self.tags)
        return super(Alert, self).render()


class AlertUtils(object):

    def equals(self, alert1, alert2):
        return (
            alert1.alert_id == alert2.alert_id and
            str(alert1.acked) == alert2.acked and
           alert_severity_map[alert1.severity] == \
               alert_severity_map[alert2.severity]
        )

    def update(self, new_alert, existing_alert):
        if (
            alert_severity_map[new_alert.severity] <= alert_severity_map[
                existing_alert.severity] and
            alert_severity_map[new_alert.severity] == alert_severity_map[
                'INFO']
        ):
            new_alert.ackedby = "TENDRL"
            new_alert.acked = True
            new_alert.acked_at = now()
            new_alert.ack_comment = ['System acked']
        new_alert.alert_id = existing_alert.alert_id
        return new_alert

    def is_same(self, alert1, alert2):
        if alert1.resource != alert2.resource:
            return False
        if 'plugin_instance' in alert1.tags:
            if 'plugin_instance' not in alert2.tags:
                return False
            else:
                if (
                    alert1.tags['plugin_instance'] !=
                    alert2.tags['plugin_instance']
                ):
                    return False
        if 'integration_id' in alert1.tags:
            if 'integration_id' in alert2.tags:
                if (
                    alert1.tags['integration_id'] !=
                    alert2.tags['integration_id']
                ):
                    return False
            else:
                return False
        if 'integration_id' not in alert1.tags:
            if 'integration_id' in alert2.tags:
                return False
        # grafana gives cluster id for all
        if "node" in alert1.classification and alert1.node_id:
            if "node" in alert2.classification and alert2.node_id:
                if alert1.node_id != alert2.node_id:
                    return False
            else:
                return False
        elif "node" in alert2.classification and alert2.node_id:
            return False
        if alert1.alert_type != alert2.alert_type:
            return False
        if set(alert1.classification) != set(alert2.classification):
            return False
        return True

    def to_obj(self, alert_json):
        return Alert(
            alert_json['alert_id'],
            alert_json['node_id'],
            alert_json['time_stamp'],
            alert_json['resource'],
            alert_json['current_value'],
            alert_json['tags'],
            alert_json['alert_type'],
            alert_json['severity'],
            alert_json.get('classification', []),
            alert_json.get('significance', ''),
            alert_json.get('ackedby', ''),
            alert_json.get('acked', False),
            alert_json.get('ack_comment', ''),
            alert_json.get('acked_at', ''),
            alert_json['pid'],
            alert_json['source'],
            alert_json.get('delivered', False),
        )
