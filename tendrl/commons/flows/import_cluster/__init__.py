import etcd
import json

from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects import AtomExecutionFailedError


class ImportCluster(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(ImportCluster, self).__init__(*args, **kwargs)

    def run(self):
        if "Node[]" not in self.parameters:
            integration_id = self.parameters['TendrlContext.integration_id']
            _cluster_import_status = "clusters/%s/import_status" % \
                                     integration_id
            _cluster_import_job_id = "clusters/%s/import_job_id" % \
                                     integration_id

            # If cluster.import_status="failed", allow retries
            try:
                NS._int.wclient.delete(_cluster_import_status,
                                       prevValue="failed")
                NS._int.wclient.delete(_cluster_import_job_id)
            except (etcd.EtcdKeyNotFound, etcd.EtcdCompareFailed):
                pass

            _cluster = NS.tendrl.objects.Cluster(
                integration_id=NS.tendrl_context.integration_id).load()
            if (_cluster.import_job_id is not None and
                    _cluster.import_job_id != "") or _cluster.import_status \
                    in ["in_progress", "done", "failed"]:
                raise FlowExecutionFailedError(
                    "Cluster already being imported by another Job, please "
                    "wait till "
                    "the job finishes (job_id: %s) (integration_id: %s) " % (
                        _cluster.import_job_id, _cluster.integration_id
                    )
                )

            _cluster.import_status = "in_progress"
            _cluster.import_job_id = self.job_id
            _cluster.save()

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
                
                _cluster = NS.tendrl.objects.Cluster(
                    integration_id=NS.tendrl_context.integration_id
                ).load()
                _cluster.enable_volume_profiling = self.parameters[
                    'Cluster.enable_volume_profiling']
                _cluster.save()
                _tag = "provisioner/%s" % _cluster.integration_id
                _index_key = "/indexes/tags/%s" % _tag
                _node_id = json.dumps([NS.node_context.node_id])
                NS._int.wclient.write(_index_key, _node_id)
                        
        try:
            super(ImportCluster, self).run()
        except (FlowExecutionFailedError,
                AtomExecutionFailedError,
                Exception) as ex:
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=NS.tendrl_context.integration_id).load()
            _cluster.import_status = "failed"
            _errors = []
            if hasattr(ex, 'message'):
                _errors = [ex.message]
            else:
                _errors = [str(ex)]
            if _errors:
                _cluster.errors = json.dumps(_errors)
            _cluster.save()
            raise ex
