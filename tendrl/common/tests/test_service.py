from tendrl.common.utils.ansible_module_runner \
    import AnsibleExecutableGenerationFailed
from tendrl.common.utils.ansible_module_runner \
    import AnsibleRunner
from tendrl.common.utils.service \
    import Service


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
            return {"message": "started service successfully"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        result, err = service.start()
        assert result == {"message": "started service successfully"}
        assert err == ""

    def test_service_stop(self, monkeypatch):
        def mock_AnsibleRunner_constructor(obj, asnible_module_path, **attr):
            assert attr == {"name": "collectd",
                            "state": "stopped"}
            return
        monkeypatch.setattr(AnsibleRunner, '__init__',
                            mock_AnsibleRunner_constructor)

        def mock_runner_run(obj):
            return {"message": "stopped service successfully"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        result, err = service.stop()
        assert result == {"message": "stopped service successfully"}
        assert err == ""

    def test_service_reload(self, monkeypatch):
        def mock_AnsibleRunner_constructor(obj, asnible_module_path, **attr):
            assert attr == {"name": "collectd",
                            "state": "reloaded"}
            return
        monkeypatch.setattr(AnsibleRunner, '__init__',
                            mock_AnsibleRunner_constructor)

        def mock_runner_run(obj):
            return {"message": "reloaded service successfully"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        result, err = service.reload()
        assert result == {"message": "reloaded service successfully"}
        assert err == ""

    def test_service_restart(self, monkeypatch):
        def mock_AnsibleRunner_constructor(obj, asnible_module_path, **attr):
            assert attr == {"name": "collectd",
                            "state": "restarted"}
            return
        monkeypatch.setattr(AnsibleRunner, '__init__',
                            mock_AnsibleRunner_constructor)

        def mock_runner_run(obj):
            return {"message": "restarted service successfully"}, ""
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        result, err = service.restart()
        assert result == {"message": "restarted service successfully"}
        assert err == ""

    def test_service_error(self, monkeypatch):

        def mock_runner_run(obj):
            raise AnsibleExecutableGenerationFailed(
                "module_path", "arg",
                "err message"
            )
        monkeypatch.setattr(AnsibleRunner, 'run', mock_runner_run)

        service = Service("collectd")
        result, err = service.start()

        assert result == {}
        assert err == "Executabe could not be generated for module" \
            " module_path , with arguments arg. Error: err message"
