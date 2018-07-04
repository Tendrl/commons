import sys
import traceback

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
        if _cluster.is_managed == "no":
            if _cluster.current_job['job_name'] == self.__class__.__name__ \
                and _cluster.current_job['status'] == 'finished':
                    raise FlowExecutionFailedError(
                        "Cluster is already in un-managed state"
                    )
        if _cluster.current_job['status'] == 'in_progress' and \
            (
                'job_id' in _cluster.locked_by and
                _cluster.locked_by['job_id'] != ""
            ) and (
                _cluster.status in ['importing', 'unmanaging', 'expanding']
            ):
            raise FlowExecutionFailedError(
                "Another job in progress for cluster."
                " Please wait till the job finishes "
                "(job_id: %s) (integration_id: %s) " %
                (
                    _cluster.current_job['job_id'],
                    _cluster.integration_id
                )
            )

        _lock_details = {
            'node_id': NS.node_context.node_id,
            'fqdn': NS.node_context.fqdn,
            'tags': NS.node_context.tags,
            'type': NS.type,
            'job_name': self.__class__.__name__,
            'job_id': self.job_id
        }
        _cluster.locked_by = _lock_details
        _cluster.status = "unmanaging"
        _cluster.current_job = {
            'job_id': self.job_id,
            'job_name': self.__class__.__name__,
            'status': "in_progress"
        }
        _cluster.save()

        try:
            super(UnmanageCluster, self).run()
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=integration_id
            ).load()
            _cluster.status = ""
            _cluster.is_managed = "no"
            _cluster.locked_by = {}
            _cluster.errors = []
            _cluster.current_job = {
                'status': "finished",
                'job_name': self.__class__.__name__,
                'job_id': self.job_id
            }
            _cluster.save()
        except (FlowExecutionFailedError,
                AtomExecutionFailedError,
                Exception) as ex:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=integration_id
            ).load()
            _cluster.status = ""
            _cluster.locked_by = {}
            _cluster.current_job = {
                'status': "failed",
                'job_name': self.__class__.__name__,
                'job_id': self.job_id
            }
            _errors = []
            if hasattr(ex, 'message'):
                _errors = [ex.message]
            else:
                _errors = [str(ex)]
            if _errors:
                _cluster.errors = _errors
            _cluster.save()
            raise FlowExecutionFailedError(str(
                traceback.format_exception(exc_type,
                                           exc_value,
                                           exc_traceback)
            ))
