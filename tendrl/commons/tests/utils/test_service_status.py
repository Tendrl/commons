from mock import patch

from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils.service_status import ServiceStatus


def run(*args):
    if args[0]:
        return "inactive", "Error", 1
    elif not args[0]:
        return "active", "Error", 1
    else:
        return "not active", "Error", 1


def test_constructor():
    service_status = ServiceStatus("service_status")
    assert service_status.name == "service_status"


def test_status():
    service_status = ServiceStatus("service_status")
    ret, _ = service_status.status()
    assert ret is False
    with patch.object(cmd_utils.Command, 'run') as mock_run:
        mock_run.return_value = run(True)
        ret, _ = service_status.status()
        assert ret is False
    with patch.object(cmd_utils.Command, 'run') as mock_run:
        mock_run.return_value = run(False)
        ret, _ = service_status.status()
        assert ret is True


def test_exists():
    service_status = ServiceStatus("service_status")
    ret, _ = service_status.exists()
    assert ret is False
