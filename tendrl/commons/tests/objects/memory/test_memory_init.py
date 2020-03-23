import builtins
import maps
from mock import patch
import psutil

from tendrl.commons.objects.memory import Memory


def open(*args):
    raise IOError


def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    memory = Memory(memory_total=10000, swap_total=150)
    assert memory is not None
    assert memory.memory_total == 10000
    with patch.object(psutil, 'virtual_memory') as mock_VirtualMemory:
        with patch.object(psutil, 'swap_memory') as mock_SwapMemory:
            Memory()
            assert mock_VirtualMemory.called
            assert mock_SwapMemory.called


# Testing render
def test_render():
    setattr(builtins, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    memory = Memory()
    assert memory.render() is not None
