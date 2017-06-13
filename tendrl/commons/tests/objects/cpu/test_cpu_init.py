import pytest
import maps
import __builtin__
from tendrl.commons.objects.cpu import Cpu
from mock import patch
from tendrl.commons.utils.cmd_utils import Command

def getNodeCpu(*args):
    return "Testing"

def run(*args):
    return '' , "Test_err", "Test_rc"

# Testing __init__
def test_constructor():
    '''
    Testing for constructor involves checking if all needed
    variales are declared initialized
    '''
    with patch.object(Cpu, '_getNodeCpu', return_value=getNodeCpu) as mock_cpu:
        # Passing dummy values
        cpu = Cpu(architecture=1, cores_per_socket=1,
                 cpu_family=1, cpu_op_mode=1,
                 model=1, model_name=1, vendor_id=1)
        assert cpu is not None
    with patch.object(Cpu, '_getNodeCpu') as mock_cpu:
        cpu = Cpu()
        assert mock_cpu.called


# Testing _getNodeCpu()
def test_getNodeCpu():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    cpu = Cpu()
    ret = cpu._getNodeCpu()
    assert ret is not None
    with patch.object(Command,'run',run) as mock_run:
        ret = cpu._getNodeCpu()


# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 1
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict(logging_socket_path="test/path")
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    cpu = Cpu()
    assert cpu.render() is not None
