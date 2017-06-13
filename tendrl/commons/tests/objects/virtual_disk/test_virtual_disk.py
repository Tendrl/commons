import pytest
import maps
import __builtin__
from tendrl.commons.objects.virtual_disk import VirtualDisk

# Testing __init__
def test_constructor():
    '''
    Testing for constructor involves checking if all needed
    variales are declared initialized
    '''
    virtual_disk = VirtualDisk()
    assert virtual_disk.value == 'nodes/{0}/LocalStorage/Virtio/{1}'
