import json

import etcd

from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError


class ImportCluster(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(ImportCluster, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        if "Node[]" not in self.parameters:
            try:
                integration_id_index_key = \
                    "indexes/tags/tendrl/integration/%s" % integration_id
                _node_ids = NS._int.client.read(
                    integration_id_index_key).value
                self.parameters["Node[]"] = json.loads(_node_ids)
            except etcd.EtcdKeyNotFound:
                raise FlowExecutionFailedError("Cluster with "
                                               "integration_id "
                                               "(%s) not found, cannot "
                                               "import" % integration_id)

        super(ImportCluster, self).run()
