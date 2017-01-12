import etcd
import json
from mock import MagicMock
import pytest
import sys
sys.modules['tendrl.common.config'] = MagicMock()
del sys.modules['tendrl.common.config']
from tendrl.commons.alert import Alert
from tendrl.commons.alert import AlertUtils
from tendrl.commons.alert import config
import uuid


class Test_alerts_utils(object):
    def get_alert(self, resource, alert_id, severity=None, node_id=None):
        alert = {
            "alert_type": "percent_bytes",
            "resource": "%s" % resource,
            "severity": "CRITICAL",
            "tags": {
                "message": 'Host XX.YY.ZZ, plugin %s'
                'type percent_bytes (instance used): Data '
                'source \"value\" is currently 2.650770. That is above the '
                'failure threshold of 2.000000.\\n' % resource,
                "warning_max": "1.000000e+00",
                "failure_max": "2.000000e+00"
            },
            "pid": "30033",
            "acked": False,
            "ackedby": "",
            "source": "collectd",
            "alert_id": "%s" % alert_id,
            "node_id": "05694096-0a59-4d34-835a-2595770b9e56",
            "significance": "HIGH",
            "current_value": "2.650770e+00",
            "time_stamp": "1482912389.914"
        }
        if node_id is not None:
            alert['node_id'] = node_id
        if severity is not None:
            alert['severity'] = severity
        return alert

    def alert_to_etcd_alert(
        self, alert, modified_index, created_index, is_dir
    ):
        ret_val = {
            'key': "/alerts/%s" % alert['alert_id'],
            'value': json.dumps(alert),
            'expiration': None,
            'ttl': None,
            'modifiedIndex': modified_index,
            'createdIndex': created_index,
            'newKey': False,
            'dir': is_dir,
        }
        return ret_val

    def test_alertsSuccessfulValidate(self, monkeypatch):
        expected_alert = self.get_alert('memory', uuid.uuid4())

        alert = AlertUtils().validate_alert_json(expected_alert)

        def mock_config(package, parameter):
            if parameter == "etcd_port":
                return '2379'
            if parameter == 'etcd_connection':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)
        assert alert == expected_alert

    def test_alertfailurevalidation(self, monkeypatch):
        test_alert = {}

        def mock_config(package, parameter):
            if parameter == "etcd_port":
                return '2379'
            if parameter == 'etcd_connection':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)

        pytest.raises(
            KeyError,
            AlertUtils().validate_alert_json,
            test_alert
        )

    def test_get_alerts(self, monkeypatch):
        def mock_config(package, parameter):
            if parameter == "etcd_port":
                return '2379'
            if parameter == 'etcd_connection':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)
        df_alert_id = str(uuid.uuid4())
        alert1_dict = self.get_alert('df', df_alert_id)
        alert1 = AlertUtils().to_obj(alert1_dict)
        etcd_alert1 = self.alert_to_etcd_alert(alert1_dict, 5, 1, False)
        memory_alert_id = str(uuid.uuid4())
        alert2_dict = self.get_alert('memory', memory_alert_id)
        alert2 = AlertUtils().to_obj(alert2_dict)
        etcd_alert2 = self.alert_to_etcd_alert(alert2_dict, 6, 2, False)
        cpu_alert_id = str(uuid.uuid4())
        alert3_dict = self.get_alert('cpu', cpu_alert_id)
        alert3 = AlertUtils().to_obj(alert3_dict)
        etcd_alert3 = self.alert_to_etcd_alert(alert3_dict, 7, 3, False)
        swap_alert_id = str(uuid.uuid4())
        alert4_dict = self.get_alert('swap', swap_alert_id)
        alert4 = AlertUtils().to_obj(alert4_dict)
        etcd_alert4 = self.alert_to_etcd_alert(alert4_dict, 8, 4, False)

        def get_etcd_alerts(path, recursive):
            etcd_tree = {
                "node": {
                    'key': "/alerts/",
                    'expiration': None,
                    'ttl': None,
                    'modifiedIndex': 5,
                    'createdIndex': 1,
                    'newKey': False,
                    'dir': True,
                    'nodes': [
                        etcd_alert1,
                        etcd_alert2,
                        etcd_alert3,
                        etcd_alert4
                    ]
                }
            }
            return etcd.EtcdResult(**etcd_tree)

        expected_alerts = sorted(
            [alert1, alert2, alert3, alert4]
        )
        alert_utils = AlertUtils()

        monkeypatch.setattr(
            alert_utils.etcd_client,
            'read',
            get_etcd_alerts
        )
        for alert in alert_utils.get_alerts():
            matching_alert_found = False
            for e_alert in expected_alerts:
                if alert_utils.equals(alert, e_alert):
                    matching_alert_found = True
            if not matching_alert_found:
                assert False


    def test_to_obj(self, monkeypatch):
        df_alert_id = str(uuid.uuid4())
        alert_dict = self.get_alert('df', df_alert_id)

        def mock_config(package, parameter):
            if parameter == "etcd_port":
                return '2379'
            if parameter == 'etcd_connection':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)

        alert = AlertUtils().to_obj(alert_dict)
        expected_alert = Alert(
            alert_id=alert_dict["alert_id"],
            node_id=alert_dict["node_id"],
            time_stamp=alert_dict["time_stamp"],
            resource=alert_dict["resource"],
            current_value=alert_dict["current_value"],
            tags=alert_dict["tags"],
            alert_type=alert_dict["alert_type"],
            severity=alert_dict["severity"],
            significance=alert_dict["significance"],
            ackedby=alert_dict["ackedby"],
            acked=alert_dict["acked"],
            pid=alert_dict["pid"],
            source=alert_dict["source"]
        )
        assert AlertUtils().equals(alert, expected_alert)

    def test_is_same(self, monkeypatch):
        def mock_config(package, parameter):
            if parameter == "etcd_port":
                return '2379'
            if parameter == 'etcd_connection':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)
        df_alert1_id = str(uuid.uuid4())
        alert1_dict = self.get_alert(
            'df',
            df_alert1_id,
            severity='CRITICAL'
        )
        alert1 = AlertUtils().to_obj(alert1_dict)
        df_alert2_id = str(uuid.uuid4())
        alert2_dict = self.get_alert(
            'df',
            df_alert2_id,
            severity='CRITICAL'
        )
        alert2 = AlertUtils().to_obj(alert2_dict)
        assert AlertUtils().is_same(alert1, alert2)

    def test_equals(self, monkeypatch):
        def mock_config(package, parameter):
            if parameter == "etcd_port":
                return '2379'
            if parameter == 'etcd_connection':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)
        df_alert_id = str(uuid.uuid4())
        alert_dict = self.get_alert(
            'df',
            df_alert_id,
            severity='CRITICAL'
        )
        alert = AlertUtils().to_obj(alert_dict)
        assert AlertUtils().equals(alert, alert)

    def test_update(self, monkeypatch):
        def mock_config(package, parameter):
            if parameter == "etcd_port":
                return '2379'
            if parameter == 'etcd_connection':
                return '0.0.0.0'

        monkeypatch.setattr(config, 'get', mock_config)
        df_alert1_id = str(uuid.uuid4())
        alert1_dict = self.get_alert(
            'df',
            df_alert1_id,
            severity='INFO'
        )
        alert1 = AlertUtils().to_obj(alert1_dict)
        df_alert2_id = str(uuid.uuid4())
        alert2_dict = self.get_alert(
            'df',
            df_alert2_id,
            severity='CRITICAL'
        )
        alert2 = AlertUtils().to_obj(alert2_dict)
        expected_alert_dict = alert1_dict
        expected_alert_dict['node_id'] = alert1_dict['node_id']
        expected_alert_dict['ackedby'] = 'Tendrl'
        expected_alert_dict['acked'] = True
        expected_alert_dict['time_stamp'] = alert1_dict['time_stamp']
        expected_alert_dict['alert_id'] = alert2_dict['alert_id']
        result_alert_dict = AlertUtils().update(alert1, alert2)
        assert AlertUtils().equals(
            result_alert_dict,
            AlertUtils().to_obj(expected_alert_dict)
        )
