from tendrl.commons.utils.command \
    import Command
from tendrl.commons.utils.service_status \
    import ServiceStatus


class TestServiceStatus(object):
    def test_service_status_constructor(self, monkeypatch):
        service = ServiceStatus("tendrl-node-agent", '/tmp/')
        assert service.name == "tendrl-node-agent"

    def test_service_exists_true(self, monkeypatch):
        def mock_command_constructor(obj, command):
            assert command == "systemctl show -p LoadState" + \
                " tendrl-node-agent.service"
            return

        monkeypatch.setattr(Command, '__init__',
                            mock_command_constructor)

        def mock_command_run(obj, exec_path):
            stdout = "LoadState=loaded"
            stderr = ""
            rc = 0
            return stdout, stderr, rc

        monkeypatch.setattr(Command, 'run', mock_command_run)

        service = ServiceStatus("tendrl-node-agent", '/tmp/')
        exists = service.exists()
        assert exists

    def test_service_exists_false(self, monkeypatch):
        def mock_command_constructor(obj, command):
            assert command == "systemctl show -p LoadState " + \
                "tendrl-node-agent.service"
            return

        monkeypatch.setattr(Command, '__init__',
                            mock_command_constructor)

        def mock_command_run(obj, exec_path):
            stdout = ""
            stderr = ""
            rc = 1
            return stdout, stderr, rc

        monkeypatch.setattr(Command, 'run', mock_command_run)

        service = ServiceStatus("tendrl-node-agent", '/tmp/')
        exists = service.exists()
        assert not exists

    def test_service_statuss_true(self, monkeypatch):
        def mock_command_constructor(obj, command):
            assert command == "systemctl status " + \
                "tendrl-node-agent.service"
            return

        monkeypatch.setattr(Command, '__init__',
                            mock_command_constructor)

        def mock_command_run(obj, exec_path):
            stdout = "tendrl-node-agent.service - A python agent local to" + \
                     " every managed storage node in the sds cluster " + \
                     "   Loaded: loaded (/usr/lib/systemd/system/tendrl" + \
                     "-node-agent.service;disabled;vendor preset:disabled)" + \
                     " Active:active(running)since Thu 2017-01-12 19:14:32" + \
                     " IST; 15h ago  Main PID: 5216 (tendrl-node-age) " + \
                     "   CGroup: /system.slice/tendrl-node-agent.service"
            stderr = ""
            rc = 0
            return stdout, stderr, rc

        monkeypatch.setattr(Command, 'run', mock_command_run)

        service = ServiceStatus("tendrl-node-agent", '/tmp/')
        status = service.status()
        assert status

    def test_service_status_false(self, monkeypatch):
        def mock_command_constructor(obj, command):
            assert command == "systemctl status " + \
                "tendrl-node-agent.service"
            return

        monkeypatch.setattr(Command, '__init__',
                            mock_command_constructor)

        def mock_command_run(obj, exec_path):
            stdout = ""
            stderr = ""
            rc = 1
            return stdout, stderr, rc

        monkeypatch.setattr(Command, 'run', mock_command_run)

        service = ServiceStatus("tendrl-node-agent", '/tmp/')
        status = service.status()
        assert not status
