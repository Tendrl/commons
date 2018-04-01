import etcd
import json
import re

from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects import AtomExecutionFailedError


class ImportCluster(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(ImportCluster, self).__init__(*args, **kwargs)

    def run(self):
        if "Node[]" not in self.parameters:
            integration_id = self.parameters['TendrlContext.integration_id']
            short_name = self.parameters.get('Cluster.short_name', None)
            if short_name:
                if not re.match('^[a-zA-Z0-9][A-Za-z0-9_]*$', short_name):
                    raise FlowExecutionFailedError(
                        "Invalid cluster short_name: %s. "
                        "Only alpha numeric and underscore "
                        "allowed for short name" %
                        short_name
                    )
            # Check for uniqueness of cluster short name
            _clusters = NS._int.client.read(
                '/clusters'
            )
            for entry in _clusters.leaves:
                _cluster = NS.tendrl.objects.Cluster(
                    integration_id=entry.key.split('/')[-1]
                ).load()
                if _cluster.short_name and short_name and \
                    _cluster.short_name == short_name:
                    raise FlowExecutionFailedError(
                        "Cluster with name: %s already exists" % short_name
                    )
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

            if short_name not in [None, ""]:
                _cluster.short_name = short_name
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
            # Check if this job is parent and then only set status
            # This could be called from parent import cluster or
            # even from expand cluster flow. We should not set the
            # cluster's current job status from child jobs
            _job = NS.tendrl.objects.Job(job_id=self.job_id).load()
            if 'parent' not in _job.payload:
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
