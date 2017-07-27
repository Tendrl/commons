from tendrl.commons.objects.virtual_disk import VirtualDisk


def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    virtual_disk = VirtualDisk()
    assert virtual_disk.value == 'nodes/{0}/LocalStorage/Virtio/{1}'
