import builtins
import maps
import pytest


from tendrl.commons.objects.block_device import BlockDevice


# Testing __init__
def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    block_device = BlockDevice()
    assert block_device.device_name is None
    block_device = BlockDevice("Test_device")
    assert block_device.device_name == "Test_device"


# Testing render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    block_device = BlockDevice()
    with pytest.raises(AttributeError):
        block_device.render()
    block_device = BlockDevice("Test/Device")
    block_device.render()
