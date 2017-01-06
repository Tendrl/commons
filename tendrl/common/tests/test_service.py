from mock import MagicMock
import sys
sys.modules['tendrl.common.config'] = MagicMock()

from tendrl.common.utils.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.common.utils.ansible_module_runner \
    import AnsibleRunner
from tendrl.common.utils.service \
    import Service

del sys.modules['tendrl.common.config']


class TestService(object):
    def test_service_constructor(self, monkeypatch):
        service = Service("collectd", "yes")
        expected_attr = {"name": "collectd",
                         "enabled": "yes"}

        assert expected_attr == service.attributes

    def test_service_start(self, monkeypatch):
        def mock_AnsibleRunner_constructor(obj, asnible_module_path, **attr):
            assert attr == {"name": "collectd",
                            "state": "started"}
            return
        monkeypatch.setattr(AnsibleRunner, '__init__',
                            mock_AnsibleRunner_constructor)

        def mock_runner_run(obj):
            result = {
                u'state': u'started',
                u'msg': u'',
                u'invocation': {
                    u'module_args': {
                        u'name': u'collectddd',
                        u'enabled': None,
                        u'daemon_reload': False,
                        u'state': u'started',
                        u'user': False,
                        u'masked': None
                    }
                }
            }
            return result, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        message, success = service.start()
        assert message == ""
        assert success

    def test_service_stop(self, monkeypatch):
        def mock_AnsibleRunner_constructor(obj, asnible_module_path, **attr):
            assert attr == {"name": "collectd",
                            "state": "stopped"}
            return
        monkeypatch.setattr(AnsibleRunner, '__init__',
                            mock_AnsibleRunner_constructor)

        def mock_runner_run(obj):
            result = {
                u'state': u'stopped',
                u'msg': u'',
                u'invocation': {
                    u'module_args': {
                        u'name': u'collectddd',
                        u'enabled': None,
                        u'daemon_reload': False,
                        u'state': u'stopped',
                        u'user': False,
                        u'masked': None
                    }
                }
            }
            return result, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        message, success = service.stop()
        assert message == ""
        assert success

    def test_service_reload(self, monkeypatch):
        def mock_AnsibleRunner_constructor(obj, asnible_module_path, **attr):
            assert attr == {"name": "collectd",
                            "state": "reloaded"}
            return
        monkeypatch.setattr(AnsibleRunner, '__init__',
                            mock_AnsibleRunner_constructor)

        def mock_runner_run(obj):
            result = {
                u'state': u'started',
                u'msg': u'',
                u'invocation': {
                    u'module_args': {
                        u'name': u'collectddd',
                        u'enabled': None,
                        u'daemon_reload': False,
                        u'state': u'reloaded',
                        u'user': False,
                        u'masked': None
                    }
                }
            }
            return result, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        message, success = service.reload()
        assert message == ""
        assert success

    def test_service_restart(self, monkeypatch):
        def mock_AnsibleRunner_constructor(obj, asnible_module_path, **attr):
            assert attr == {"name": "collectd",
                            "state": "restarted"}
            return
        monkeypatch.setattr(AnsibleRunner, '__init__',
                            mock_AnsibleRunner_constructor)

        def mock_runner_run(obj):
            result = {
                u'state': u'started',
                u'msg': u'',
                u'invocation': {
                    u'module_args': {
                        u'name': u'collectddd',
                        u'enabled': None,
                        u'daemon_reload': False,
                        u'state': u'restarted',
                        u'user': False,
                        u'masked': None
                    }
                }
            }
            return result, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        message, success = service.restart()
        assert message == ""
        assert success

    def test_service_error(self, monkeypatch):

        def mock_runner_run(obj):
            raise AnsibleExecutableGenerationFailed(
                "module_path", "arg",
                "err message"
            )
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        message, success = service.start()

        assert not success
        assert message == "Executabe could not be generated for module" \
            " module_path , with arguments arg. Error: err message"
