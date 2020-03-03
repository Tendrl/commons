import builtins
import maps
from mock import patch

from tendrl.commons.objects.service import Service
from tendrl.commons.utils import cmd_utils


def run(*args):
    return 'LoadState=loaded', 'No Error', 0


def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    service = Service()
    assert service.exists is False
    assert service.running is False


def test_get_service_info():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    service = Service()
    with patch.object(cmd_utils.Command, "run") as mock_run:
        mock_run.return_value = run()
        ret = service.get_service_info("Test_service")
        assert ret['exists'] is True


def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    service = Service(service="@*Test")
    assert service.render() is not None
