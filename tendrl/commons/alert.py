from ruamel import yaml

from tendrl.commons.singleton import to_singleton

alert_severity_map = {
    'INFO': 0,
    'WARNING': 1,
    'CRITICAL': 2
}


class Alert(object):

    def __init__(self, alert_id, node_id, time_stamp, resource, current_value,
                 tags, alert_type, severity, significance, ackedby, acked,
                 pid, source):
        self.alert_id = alert_id
        self.node_id = node_id
        self.time_stamp = time_stamp
        self.resource = resource
        self.current_value = current_value
        self.tags = tags
        self.alert_type = alert_type
        self.severity = severity
        self.significance = significance
        self.ackedby = ackedby
        self.acked = acked
        self.pid = pid
        self.source = source

    def to_json_string(self):
        return yaml.safe_dump(self.__dict__)


@to_singleton
class AlertUtils(object):
    def __init__(self, etcd_client):
        self.etcd_client = etcd_client

    def validate_alert_json(self, alert):
        if 'time_stamp' not in alert:
            raise KeyError('time_stamp')
        if 'resource' not in alert:
            raise KeyError('resource')
        if 'severity' not in alert:
            raise KeyError('severity')
        if 'source' not in alert:
            raise KeyError('source')
        if 'current_value' not in alert:
            raise KeyError('current_value')
        if 'alert_type' not in alert:
            raise KeyError('alert_type')
        return alert

    def store_alert(self, alert):
        self.etcd_client.write(
            '/alerts/%s' % alert.alert_id,
            alert.to_json_string()
        )

    def get_alerts(self):
        alerts_arr = []
        alerts = self.etcd_client.read('/alerts', recursive=True)
        for child in alerts._children:
            alerts_arr.append(self.to_obj(yaml.safe_load(child['value'])))
        return alerts_arr

    def to_obj(self, alert_json):
        alert_json = self.validate_alert_json(alert_json)
        return Alert(
            alert_id=alert_json["alert_id"],
            node_id=alert_json["node_id"],
            time_stamp=alert_json["time_stamp"],
            resource=alert_json["resource"],
            current_value=alert_json["current_value"],
            tags=alert_json["tags"],
            alert_type=alert_json["alert_type"],
            severity=alert_json["severity"],
            significance=alert_json["significance"],
            ackedby=alert_json["ackedby"],
            acked=alert_json["acked"],
            pid=alert_json["pid"],
            source=alert_json["source"]
        )

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
        if 'Tendrl_context.cluster_id' in alert1.tags:
            if 'Tendrl_context.cluster_id' in alert2.tags:
                if (
                    alert1.tags['Tendrl_context.cluster_id'] !=
                    alert2.tags['Tendrl_context.cluster_id']
                ):
                    return False
            else:
                return False
        if 'Tendrl_context.cluster_id' not in alert1.tags:
            if 'Tendrl_context.cluster_id' in alert2.tags:
                return False
            if alert1.node_id != alert2.node_id:
                return False
        if alert1.alert_type != alert2.alert_type:
            return False
        return True

    def equals(self, alert1, alert2):
        return (
            alert1.alert_id == alert2.alert_id and
            alert1.node_id == alert2.node_id and
            alert1.time_stamp == alert2.time_stamp and
            alert1.resource == alert2.resource and
            alert1.current_value == alert2.current_value and
            alert1.tags == alert2.tags and
            alert1.alert_type == alert2.alert_type and
            alert1.severity == alert2.severity and
            alert1.significance == alert2.significance and
            alert1.ackedby == alert2.ackedby and
            alert1.acked == alert2.acked and
            alert1.pid == alert2.pid and
            alert1.source == alert2.source
        )

    def update(self, alert1, existing_alert):
        time_stamp = existing_alert.time_stamp
        if (
            alert_severity_map[alert1.severity] < alert_severity_map[
                existing_alert.severity] and
            alert_severity_map[alert1.severity] == alert_severity_map[
                'INFO']
        ):
            time_stamp = alert1.time_stamp
            alert1.ackedby = 'Tendrl'
            alert1.acked = True
        alert1.alert_id = existing_alert.alert_id
        alert1.time_stamp = time_stamp
        return alert1
