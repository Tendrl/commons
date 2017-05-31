import etcd

from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError


class IsNodeTendrlManaged(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(IsNodeTendrlManaged, self).__init__(*args, **kwargs)

    def run(self):
        node_ids = self.parameters.get('Node[]')
        if not node_ids or len(node_ids) == 0:
            raise AtomExecutionFailedError("Node[] cannot be empty")

        for node_id in node_ids:
            # Check if node has the OS details populated
            try:
                os_details = NS._int.client.read("nodes/%s/Os" % node_id)
                if os_details.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node doesnt have OS details populated"
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node doesnt have OS details populated"
                )

            # Check if node has the CPU details populated
            try:
                cpu_details = NS._int.client.read("nodes/%s/Cpu" % node_id)
                if cpu_details.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node doesnt have CPU details populated"
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node doesnt have CPU details populated"
                )

            # Check if node has the Memory populated
            try:
                memory_details = NS._int.client.read("nodes/%s/Memory" % node_id)
                if memory_details.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node doesnt have Memory details populated"
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node doesnt have Memory details populated"
                )

            # Check if node has the block devices populated
            try:
                block_devices = NS._int.client.read("nodes/%s/BlockDevices" % node_id)
                if block_devices.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node doesnt have block device details populated"
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node doesnt have block device details populated"
                )

            # Check if node has the disks data populated
            try:
                disks = NS._int.client.read("nodes/%s/Disks" % node_id)
                # If disks have no child nodes, error out
                if disks.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node doesnt have disks details populated"
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node doesnt have disks details populated"
                )

            # Check if node has networks details populated
            try:
                networks = NS._int.client.read("nodes/%s/Networks" % node_id)
                if networks.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node doesnt have network details populated"
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node doesnt have network details populated"
                )

        return True
