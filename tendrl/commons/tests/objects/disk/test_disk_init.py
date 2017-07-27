import __builtin__
import maps
import pytest


from tendrl.commons.objects.disk import Disk


# Testing __init__
def test_constructor():
    '''Testing for constructor involves checking if all needed

    variables are declared initialized
    '''
    disk = Disk()
    assert disk.disk_id is None
    # Passing Dummy Values
    disk = Disk(
        disk_id="M-Test-Disk-Id", hardware_id=172, disk_name="Test Disk",
        sysfs_id="Test System", sysfs_busid=1, sysfs_device_link="",
        hardware_class=None, model="M34", vendor=None, device=None,
        rmversion=None, serial_no=None, driver=None, driver_modules=None,
        device_files=None, device_number=12, bios_id=None,
        geo_bios_edd=None, geo_logical=None, size=None, size_bios_edd=None,
        geo_bios_legacy=None, config_status=None, partitions=None)
    assert disk.model == "M34"


def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1
    disk = Disk()
    with pytest.raises(AttributeError):
        disk.render()
    disk = Disk("Test-Disk")
    disk.render()
