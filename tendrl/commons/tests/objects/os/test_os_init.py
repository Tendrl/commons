import pytest
import maps
import __builtin__
from tendrl.commons.objects.os import Os

# Testing __init__
def test_constructor():
    '''
    Testing for constructor involves checking if all needed
    variales are declared initialized
    '''
    os = Os()
    assert os is not None
    os = Os(kernel_version=1.1, os="Centos",
            os_version=17.2, selinux_mode="Test")
    assert os.selinux_mode == "Test"

def test_getNodeOs():
    os = Os()
    assert os._getNodeOs() is not None

# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    os = Os()
    assert os.render() is not None
