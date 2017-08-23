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
            else:
                # TODO(shtripat) ceph-installer is auto detected and
                #  provisioner/$integration_id
                # tag is set , below is not required for ceph
                current_tags = list(NS.node_context.tags)
                new_tags = ['provisioner/%s' % integration_id]
                new_tags += current_tags
                new_tags = list(set(new_tags))
                if new_tags != current_tags:
                    NS.node_context.tags = new_tags
                    NS.node_context.save()

                _cluster = NS.tendrl.objects.Cluster(integration_id=NS.tendrl_context.integration_id).load()
                _cluster.enable_volume_profiling = self.parameters['Cluster.enable_volume_profiling']
                _cluster.save()


        super(ImportCluster, self).run()
