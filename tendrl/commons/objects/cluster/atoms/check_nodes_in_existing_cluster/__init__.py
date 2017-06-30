import etcd
import gevent

from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError


class CheckNodesInExistingCluster(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(CheckNodesInExistingCluster, self).__init__(*args, **kwargs)

    def run(self):
        if not self.parameters.get('import_after_expand', False) and \
            not self.parameters.get('import_after_create', False):
            # Above condition means, this is a fresh import
            # Check if nodes participate in some existing cluster
            try:
                for entry in self.parameters["Node[]"]:
                    _node_tc = NS.tendrl.objects.TendrlContext(
                        node_id=entry
                    ).load()
                    Event(
                        Message(
                            job_id=self.parameters['job_id'],
                            flow_id = self.parameters['flow_id'],
                            priority="info",
                            publisher=NS.publisher_id,
                            payload={
                                "message": "Check: Node %s not part of any other cluster" % entry
                            }
                        )
                    )

                    if _node_tc.integration_id != "":
                        _msg = "Error: Node %s is already part of other " \
                               "cluster %s" % (entry, _node_tc.integration_id)
                        Event(
                            Message(
                                job_id=self.parameters['job_id'],
                                flow_id = self.parameters['flow_id'],
                                priority="error",
                                publisher=NS.publisher_id,
                                payload={"message": _msg}
                            )
                        )
                        return False
            except etcd.EtcdKeyNotFound:
                raise AtomExecutionFailedError(
                    "Error while checking pre-participation of nodes in any cluster"
                )

        return True
