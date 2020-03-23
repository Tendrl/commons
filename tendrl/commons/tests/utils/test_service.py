import builtins
import maps
from mock import patch
import pytest


from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils.service import Service


def ansible_run(*args):
    if args[0]:
        return {"msg": "test_msg", "state": "started"}, "Error"
    else:
        return {"msg": "test_msg", "state": "stopped"}, "Error"


def run(*args):
    NS.pop('publisher_id')
    raise ansible_module_runner.AnsibleExecutableGenerationFailed("Error")


def ansible(*args, **kwargs):
    raise ansible_module_runner.AnsibleModuleNotFound


def init():
    setattr(builtins, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['logging_socket_path'] = "test"
    NS["node_context"] = maps.NamedDict()
    NS.node_context["node_id"] = 1


def test_constructor():
    service = Service("Test_service", "node_context", 1, True)
    assert service.publisher_id == "node_context"
    assert service.attributes["name"] == "Test_service"
    assert service.attributes["enabled"] is True
    init()
    service = Service("Test_service")
    assert service.node_id == 1


def test_start():
    init()
    service = Service("Test_service")
    service.start()
    with patch.object(ansible_module_runner, 'AnsibleRunner', ansible):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            ret = service.start()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run', run):
        ret = service.start()
        assert ret[1] is False
    with patch.object(ansible_module_runner.AnsibleRunner, 'run') as mock_run:
        mock_run.return_value = ansible_run(True)
        ret = service.start()
        assert ret[1] is True
        assert ret[0] == "test_msg"


def test_stop():
    init()
    service = Service("Test_service")
    service.stop()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run') as mock_run:
        mock_run.return_value = ansible_run(False)
        ret = service.stop()
        assert ret[1] is True


def test_reload():
    init()
    service = Service("Test_service")
    service.reload()
    with patch.object(ansible_module_runner.AnsibleRunner, 'run') as mock_run:
        mock_run.return_value = ansible_run(False)
        ret = service.reload()
        assert ret[1] is False


def test_restart():
    init()
    service = Service("Test_service")
    with patch.object(ansible_module_runner, 'AnsibleRunner', ansible):
        with pytest.raises(ansible_module_runner.AnsibleModuleNotFound):
            service.restart()
