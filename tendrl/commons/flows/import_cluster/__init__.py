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
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=NS.tendrl_context.integration_id).load()
            if (_cluster.status is not None and
                    _cluster.status != "" and
                    _cluster.current_job['status'] == 'in_progress' and
                    _cluster.status in
                    ["importing", "unmanaging", "expanding"]):
                raise FlowExecutionFailedError(
                    "Another job in progress for cluster, please wait till "
                    "the job finishes (job_id: %s) (integration_id: %s) " % (
                        _cluster.current_job['job_id'],
                        _cluster.integration_id
                    )
                )

            _cluster.status = "importing"
            _cluster.current_job = {
                'job_id': self.job_id,
                'job_name': self.__class__.__name__,
                'status': 'in_progress'
            }
            _cluster.save()

            try:
                integration_id_index_key = \
                    "indexes/tags/tendrl/integration/%s" % integration_id
                _node_ids = NS._int.client.read(
                    integration_id_index_key).value
                self.parameters["Node[]"] = json.loads(_node_ids)
            except etcd.EtcdKeyNotFound:
                _cluster = NS.tendrl.objects.Cluster(
                    integration_id=NS.tendrl_context.integration_id).load()
                _cluster.status = ""
                _cluster.current_job['status'] = 'failed'
                _cluster.save()
                raise FlowExecutionFailedError("Cluster with "
                                               "integration_id "
                                               "(%s) not found, cannot "
                                               "import" % integration_id)
            else:
                _cluster = NS.tendrl.objects.Cluster(
                    integration_id=NS.tendrl_context.integration_id
                ).load()
                _cluster.volume_profiling_flag = self.parameters[
                    'Cluster.volume_profiling_flag']
                _cluster.save()

        try:
            super(ImportCluster, self).run()
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=NS.tendrl_context.integration_id
            ).load()
            _cluster.status = ""
            _cluster.current_job['status'] = "finished"
            _cluster.is_managed = "yes"
            _cluster.save()
        except (FlowExecutionFailedError,
                AtomExecutionFailedError,
                Exception) as ex:
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=NS.tendrl_context.integration_id).load()
            _cluster.status = ""
            _cluster.current_job['status'] = 'failed'
            _errors = []
            if hasattr(ex, 'message'):
                _errors = [ex.message]
            else:
                _errors = [str(ex)]
            if _errors:
                _cluster.errors = _errors
            _cluster.save()
            raise ex
