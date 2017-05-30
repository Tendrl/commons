import pytest
import maps
import __builtin__
from tendrl.commons.objects.node_network import NodeNetwork


# Testing __init__
def test_constructor():
    '''
    Testing for constructor involves checking if all needed
    variales are declared initialized
    '''
    node_network = NodeNetwork()
    assert node_network.interface is None
    
    #Passing Dummy Values
    node_network = NodeNetwork(interface="Test_interface", interface_id=1,
                               interface_type="Test", model="M4")
    assert node_network.interface == "Test_interface"

# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    node_network = NodeNetwork()
    assert node_network.render() is not None
