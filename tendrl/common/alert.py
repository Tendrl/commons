import etcd
import json
from tendrl.common.config import TendrlConfig
from tendrl.common.singleton import to_singleton

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
        return json.dumps(self.__dict__)

    def is_same(self, alert2):
        if self.resource != alert2.resource:
            return False
        if self.alert_type != alert2.alert_type:
            return False
        if 'Tendrl_context.cluster_id' in self.tags:
            if 'Tendrl_context.cluster_id' in alert2.tags:
                if (
                    self.tags['Tendrl_context.cluster_id'] !=
                    alert2.tags['Tendrl_context.cluster_id']
                ):
                    return False
            else:
                return False
        if 'Tendrl_context.cluster_id' not in self.tags:
            if 'Tendrl_context.cluster_id' in alert2.tags:
                return False
            if self.node_id != alert2.node_id:
                return False
        if 'plugin_instance' in self.tags:
            if 'plugin_instance' not in alert2.tags:
                False
            else:
                if (
                    self.tags['plugin_instance'] !=
                    alert2.tags['plugin_instance']
                ):
                    return False
        return True

    def update(self, existing_alert):
        if (
            alert_severity_map[self.severity] < alert_severity_map[
                existing_alert.severity] and
            alert_severity_map[self.severity] == alert_severity_map[
                'INFO']
        ):
            self.ackedby = 'Tendrl'
            self.acked = True

    @staticmethod
    def to_obj(json_str):
        return Alert(**json.loads(json_str))


@to_singleton
class AlertUtils(object):
    def __init__(self):
        config = TendrlConfig()
        etcd_kwargs = {
            'port': int(config.get("common", "etcd_port")),
            'host': config.get("common", "etcd_connection")
        }
        self.etcd_client = etcd.Client(**etcd_kwargs)

    def validate_alert_json(self, alert_data):
        alert = json.loads(alert_data)
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
