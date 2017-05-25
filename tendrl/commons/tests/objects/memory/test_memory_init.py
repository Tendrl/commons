import pytest
import maps
import __builtin__
from tendrl.commons.objects.memory import Memory
from mock import patch

def open(*args):
    raise IOError
# Testing __init__
def test_constructor():
    '''
    Testing for constructor involves checking if all needed
    variales are declared initialized
    '''
    memory = Memory(total_size=10000, swap_total=150)
    assert memory is not None
    assert memory.total_size == 10000
    with patch.object(Memory, '_getNodeMemory') as mock_getNodeMemory:
        memory = Memory()
        assert mock_getNodeMemory.called

# Testing _getNodeCpu()
def test_getNodeMemory():
    memory = Memory()
    ret = memory._getNodeMemory()
    assert ret is not None
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = "node_agent"
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    with patch.object(__builtin__,"open",open) as mock_open:
            memory._getNodeMemory()


# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    memory = Memory()
    assert memory.render() is not None
