
from tendrl.commons.objects.disk import Disk


class VirtualDisk(Disk):
    def __init__(self, disk_id=None, hardware_id=None,
                 disk_name=None, sysfs_id=None, sysfs_busid=None,
                 sysfs_device_link=None, hardware_class=None,
                 model=None, vendor=None, device=None,
                 rmversion=None, serial_no=None, driver=None,
                 driver_modules=None, device_files=None,
                 device_number=None, bios_id=None,
                 geo_bios_edd=None, geo_logical=None, size=None,
                 size_bios_edd=None, geo_bios_legacy=None,
                 config_status=None, partitions=None,
                 *args, **kwargs):
        super(VirtualDisk, self).__init__(
            disk_id, hardware_id, disk_name, sysfs_id, sysfs_busid,
            sysfs_device_link, hardware_class, model, vendor, device,
            rmversion, serial_no, driver, driver_modules, device_files,
            device_number, bios_id, geo_bios_edd, geo_logical, size,
            size_bios_edd, geo_bios_legacy, config_status, partitions,
            *args, **kwargs)
        self.value = 'nodes/{0}/LocalStorage/Virtio/{1}'
