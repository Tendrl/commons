
from tendrl.commons import objects


class Disk(objects.BaseObject):
    def __init__(self, disk_id=None, hardware_id=None, disk_name=None,
                 sysfs_id=None, sysfs_busid=None, sysfs_device_link=None,
                 hardware_class=None, model=None, vendor=None, device=None,
                 rmversion=None, serial_no=None, driver=None, driver_modules=None,
                 device_files=None, device_number=None, bios_id=None,
                 geo_bios_edd=None, geo_logical=None, size=None, size_bios_edd=None,
                 geo_bios_legacy=None, config_status=None, partitions=None,
                 *args, **kwargs):
        super(Disk, self).__init__(*args, **kwargs)
        self.disk_id = disk_id
        self.hardware_id = hardware_id
        self.disk_name = disk_name
        self.sysfs_id = sysfs_id
        self.sysfs_busid = sysfs_busid
        self.sysfs_device_link = sysfs_device_link
        self.hardware_class = hardware_class
        self.model = model
        self.vendor = vendor
        self.device = device
        self.rmversion = rmversion
        self.serial_no = serial_no
        self.driver = driver
        self.driver_modules = driver_modules
        self.device_files = device_files
        self.device_number = device_number 
        self.bios_id = bios_id
        self.geo_bios_edd = geo_bios_edd
        self.geo_logical = geo_logical
        self.size = size
        self.size_bios_edd = size_bios_edd
        self.geo_bios_legacy = geo_bios_legacy
        self.config_status = config_status
        self.partitions = partitions
        self.value = 'nodes/{0}/Disks/{1}'

    def render(self):
        self.value = self.value.format(NS.node_context.node_id,
                                       self.disk_id.replace('-', '_')
                                       )
        return super(Disk, self).render()
