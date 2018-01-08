import etcd
import time

from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects import AtomExecutionFailedError


class UnmanageCluster(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(UnmanageCluster, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        _cluster = NS.tendrl.objects.Cluster(
            integration_id=integration_id
        ).load()
        if _cluster.status is not None and \
            _cluster.status != "" and \
            _cluster.status in \
            ['syncing', 'importing', 'unmanaging']:
            raise FlowExecutionFailedError(
                "Another job in progress for cluster"
                "please wait till the job finishes "
                "(job_id: %s) (integration_id: %s) " %
                (
                    _cluster.current_job['job_id'],
                    _cluster.integration_id
                )
            )

        _cluster.status = "unmanaging"
        _cluster.current_job = {
            'job_id': self.job_id,
            'job_name': self.__class__.__name__,
            'status': "in_progress"
        }
        _cluster.save()

        try:
            super(UnmanageCluster, self).run()
            # Wait for cluster to re-appear as detected cluster
            # as node-agents are still running on the storage nodes
            while True:
                try:
                    _cluster = NS.tendrl.objects.Cluster(
                        integration_id=integration_id
                    ).load()
                    if _cluster.is_managed == "no":
                        break
                except etcd.EtcdKeyNotFound:
                    time.sleep(5)
                    continue
            _cluster.status = ""
            _cluster.current_job['status'] = "done"
            _cluster.save()
        except (FlowExecutionFailedError,
                AtomExecutionFailedError,
                Exception) as ex:
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=integration_id
            ).load()
            _cluster.current_job['status'] = "failed"
            _errors = []
            if hasattr(ex, 'message'):
                _errors = [ex.message]
            else:
                _errors = [str(ex)]
            if _errors:
                _cluster.errors = _errors
            _cluster.save()
            raise ex
