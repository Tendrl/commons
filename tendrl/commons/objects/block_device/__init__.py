from tendrl.commons import objects


class BlockDevice(objects.BaseObject):
    def __init__(self, device_name=None, device_kernel_name=None,
                 parent_name=None, major_to_minor_no=None, fstype=None,
                 mount_point=None, label=None, fsuuid=None,
                 read_ahead=None, read_only=None, removable_device=None,
                 size=None, state=None, owner=None, group=None,
                 mode=None, alignment=None, min_io_size=None,
                 optimal_io_size=None, phy_sector_size=None,
                 log_sector_size=None, device_type=None,
                 scheduler_name=None, req_queue_size=None,
                 discard_align_offset=None, discard_granularity=None,
                 discard_max_bytes=None, discard_zeros_data=None,
                 used=None, rotational=None, ssd=None,
                 disk_id=None, *args, **kwargs):
        super(BlockDevice, self).__init__(*args, **kwargs)
        self.device_name = device_name
        self.device_kernel_name = device_kernel_name
        self.parent_name = parent_name
        self.disk_id = disk_id
        self.major_to_minor_no = major_to_minor_no
        self.fstype = fstype
        self.mount_point = mount_point
        self.label = label
        self.fsuuid = fsuuid
        self.read_ahead = read_ahead
        self.read_only = read_only
        self.removable_device = removable_device
        self.size = size
        self.state = state
        self.owner = owner
        self.group = group
        self.mode = mode
        self.alignment = alignment
        self.min_io_size = min_io_size
        self.optimal_io_size = optimal_io_size
        self.phy_sector_size = phy_sector_size
        self.log_sector_size = log_sector_size
        self.device_type = device_type
        self.scheduler_name = scheduler_name
        self.req_queue_size = req_queue_size
        self.discard_align_offset = discard_align_offset
        self.discard_granularity = discard_granularity
        self.discard_max_bytes = discard_max_bytes
        self.discard_zeros_data = discard_zeros_data
        self.used = used
        self.rotational = rotational
        self.ssd = ssd
        self.value = 'nodes/{0}/BlockDevices/all/{1}'

    def render(self):
        self.value = self.value.format(
            NS.node_context.node_id,
            self.device_name.replace("/", "_").replace("_", "", 1))
        return super(BlockDevice, self).render()

