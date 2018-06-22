import etcd

from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.utils import etcd_utils


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
                os_details = etcd_utils.read("nodes/%s/Os" % node_id)
                if os_details.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node %s doesn't have OS details populated" %
                        NS.node_context.fqdn
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node %s doesn't have OS details populated" %
                    NS.node_context.fqdn
                )

            # Check if node has the CPU details populated
            try:
                cpu_details = etcd_utils.read("nodes/%s/Cpu" % node_id)
                if cpu_details.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node %s doesn't have CPU details populated" %
                        NS.node_context.fqdn
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node %s doesn't have CPU details populated" %
                    NS.node_context.fqdn
                )

            # Check if node has the Memory populated
            try:
                memory_details = etcd_utils.read(
                    "nodes/%s/Memory" % node_id
                )
                if memory_details.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node %s doesn't have Memory details populated" %
                        NS.node_context.fqdn
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node %s doesn't have Memory details populated" %
                    NS.node_context.fqdn
                )

            # Check if node has networks details populated
            try:
                networks = etcd_utils.read("nodes/%s/Networks" % node_id)
                if networks.leaves is None:
                    raise AtomExecutionFailedError(
                        "Node %s doesn't have network details populated" %
                        NS.node_context.fqdn
                    )
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Node %s doesn't have network details populated" %
                    NS.node_context.fqdn
                )

        return True
