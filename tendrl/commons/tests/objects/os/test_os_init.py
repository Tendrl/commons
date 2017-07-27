import __builtin__
import maps


from tendrl.commons.objects.os import Os


# Testing __init__
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
    os = Os()
    assert os is not None
    os = Os(kernel_version=1.1, os="Centos",
            os_version=17.2, selinux_mode="Test")
    assert os.selinux_mode == "Test"


def test_getNodeOs():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    os = Os()
    assert os._getNodeOs() is not None


# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    os = Os()
    assert os.render() is not None
