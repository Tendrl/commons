import etcd
import time

from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError


class IsClusterImportReady(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(IsClusterImportReady, self).__init__(*args, **kwargs)

    def run(self):
        #import pdb; pdb.set_trace()
        integration_id = self.parameters['TendrlContext.integration_id']

        # Wait for /indexes/tags/tendrl/integration/$integration_id
        # to appear. This means cluster is import ready
        wait_count = 6
        loop_count = 0
        while True:
            try:
                integration_id_index_key = \
                    "indexes/tags/tendrl/integration/%s" % integration_id
                _node_ids = NS._int.client.read(
                    integration_id_index_key
                ).value
                if _node_ids:
                    return True
                if loop_count >= wait_count:
                    raise AtomExecutionFailedError(
                        "Cluster: %s is not yet marked as "
                        "import ready. Timing out." %
                        integration_id
                    )
            except etcd.EtcdKeyNotFound:
                time.sleep(5)
                loop_count += 1
                continue
        return True
