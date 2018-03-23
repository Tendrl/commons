import json
import time
import uuid

import etcd

from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class ExpandClusterWithDetectedPeers(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(
            ExpandClusterWithDetectedPeers,
            self
        ).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        _cluster = NS.tendrl.objects.Cluster(
            integration_id=integration_id
        ).load()
        if _cluster.status is not None and _cluster.status != "" and \
            _cluster.status in ["importing", "unmanaging", "expanding"]:
            raise FlowExecutionFailedError(
                "Another job in progress for cluster, please wait till "
                "the job finishes (job_id: %s) (integration_id: %s) " % (
                    _cluster.current_job['job_id'],
                    integration_id
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
        _cluster.status = "expanding"
        _cluster.current_job = {
            'job_id': self.job_id,
            'job_name': self.__class__.__name__,
            'status': 'in_progress'
        }
        _cluster.save()

        try:
            integration_id_index_key = \
                "indexes/tags/tendrl/integration/%s" % integration_id
            node_ids = etcd_utils.read(
                integration_id_index_key).value
            node_ids = json.loads(node_ids)
        except etcd.EtcdKeyNotFound:
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=integration_id
            ).load()
            _cluster.locked_by = {}
            _cluster.status = ""
            _cluster.current_job = {
                'job_id': self.job_id,
                'job_name': self.__class__.__name__,
                'status': 'failed'
            }
            _cluster.save()

            raise FlowExecutionFailedError(
                "Cluster with integration_id "
                "(%s) not found, cannot "
                "import" % integration_id
            )

        job_ids = []
        new_peers = []
        # Remove the current node from list as its already participating
        # in cluster for sure
        node_ids.remove(NS.node_context.node_id)
        for node_id in node_ids:
            _cnc = NS.tendrl.objects.ClusterNodeContext(
                node_id=node_id
            ).load()
            if _cnc.is_managed not in [None, ""] \
                and _cnc.is_managed.lower() == "yes":
                continue

            params = {
                'TendrlContext.integration_id': integration_id,
                'Node[]': [node_id],
                'Cluster.volume_profiling_flag':
                _cluster.volume_profiling_flag
            }
            payload = {
                "tags": ["tendrl/node_%s" % node_id],
                "run": "tendrl.flows.ImportCluster",
                "status": "new",
                "parent": self.parameters['job_id'],
                "parameters": params,
                "type": "node"
            }
            _job_id = str(uuid.uuid4())
            Job(job_id=_job_id, status="new", payload=payload).save()
            logger.log(
                "info",
                NS.publisher_id,
                {
                    "message": "Importing (job: %s) Node %s "
                    "to cluster %s" % (
                        _job_id,
                        node_id,
                        integration_id
                    )
                },
                job_id=self.parameters['job_id']
            )
            job_ids.append(_job_id)
            new_peers.append(node_id)

        loop_count = 0
        # Wait for (no of nodes) * 6 minutes for import to complete
        wait_count = len(job_ids) * 36
        while True:
            if loop_count >= wait_count:
                logger.log(
                    "info",
                    NS.publisher_id,
                    {
                        "message": "Import jobs not yet complete "
                        "on all new nodes. Timing out. (%s, %s)" %
                        (str(node_ids), integration_id)
                    },
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                _cluster = NS.tendrl.objects.Cluster(
                    integration_id=integration_id
                ).load()
                _cluster.locked_by = {}
                _cluster.status = ""
                _cluster.current_job = {
                    'job_id': self.job_id,
                    'job_name': self.__class__.__name__,
                    'status': 'failed'
                }
                _cluster.save()
                return False
            time.sleep(10)
            finished = True
            for job_id in job_ids:
                job = Job(job_id=job_id).load()
                if job.status != "finished":
                    finished = False
                    break
            if finished:
                break
            else:
                loop_count += 1
                continue

        _cluster = NS.tendrl.objects.Cluster(
            integration_id=integration_id
        ).load()
        _cluster.status = ""
        _cluster.locked_by = {}
        _cluster.current_job = {
            'status': "finished",
            'job_name': self.__class__.__name__,
            'job_id': self.job_id
        }
        _cluster.save()

        logger.log(
            "info",
            NS.publisher_id,
            {
                "message": "Newly detected node(s) added to the cluster."
                "(nodes: %s) (integration_id: %s)" % (
                    str(new_peers),
                    integration_id
                ),
            },
            job_id=self.parameters['job_id'],
            flow_id=self.parameters['flow_id']
        )
        return True
