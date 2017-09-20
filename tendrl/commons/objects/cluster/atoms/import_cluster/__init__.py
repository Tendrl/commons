import gevent
import re
import uuid

from tendrl.commons.event import Event
from tendrl.commons.flows.create_cluster import utils as create_cluster_utils
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.import_cluster.gluster_help import import_gluster
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message
from tendrl.commons import objects
from tendrl.commons.objects.job import Job


class ImportCluster(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(ImportCluster, self).__init__(*args, **kwargs)

    def run(self):
        try:
            integration_id = self.parameters['TendrlContext.integration_id']

            # Lock nodes
            create_cluster_utils.acquire_node_lock(self.parameters)
            NS.tendrl_context = NS.tendrl_context.load()

            # TODO(team) when Tendrl supports create/expand/shrink cluster
            # setup passwordless ssh for all gluster nodes with given
            # integration_id (check
            # /indexes/tags/tendrl/integration/$integration_id for list of
            # nodes in cluster

            node_list = self.parameters['Node[]']
            cluster_nodes = []
            if len(node_list) > 1:
                # This is the master node for this flow
                for node in node_list:
                    if NS.node_context.node_id != node:
                        new_params = self.parameters.copy()
                        new_params['Node[]'] = [node]
                        # create same flow for each node in node list except
                        #  $this
                        payload = {"tags": ["tendrl/node_%s" % node],
                                   "run": "tendrl.flows.ImportCluster",
                                   "status": "new",
                                   "parameters": new_params,
                                   "parent": self.parameters['job_id'],
                                   "type": "node"
                                   }
                        _job_id = str(uuid.uuid4())
                        cluster_nodes.append(_job_id)
                        Job(job_id=_job_id,
                            status="new",
                            payload=payload).save()
                        Event(
                            Message(
                                job_id=self.parameters['job_id'],
                                flow_id=self.parameters['flow_id'],
                                priority="info",
                                publisher=NS.publisher_id,
                                payload={
                                    "message": "Importing (job: %s) Node %s "
                                               "to cluster %s" %
                                    (_job_id, node, integration_id)
                                }
                            )
                        )
            # Check if minimum required version of underlying gluster
            # cluster met. If not fail the import task
            cluster_ver = \
                NS.tendrl_context.sds_version.split('.')
            maj_ver = cluster_ver[0]
            min_ver = re.findall(r'\d+', cluster_ver[1])[0]
            reqd_gluster_ver = NS.compiled_definitions.get_parsed_defs()[
                'namespace.tendrl'
            ]['min_reqd_gluster_ver']
            req_maj_ver, req_min_ver, req_rel = reqd_gluster_ver.split('.')
            Event(
                Message(
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Check: Minimum required version ("
                                   "%s.%s.%s) of Gluster Storage" %
                        (req_maj_ver, req_min_ver, req_rel)
                    }
                )
            )
            ver_check_failed = False
            if int(maj_ver) < int(req_maj_ver):
                ver_check_failed = True
            else:
                if int(maj_ver) == int(req_maj_ver) and \
                        int(min_ver) < int(req_min_ver):
                        ver_check_failed = True

            if ver_check_failed:
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id'],
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={
                            "message": "Error: Minimum required version "
                                       "(%s.%s.%s) "
                            "doesnt match that of detected Gluster "
                                       "Storage (%s.%s.%s)" %
                            (req_maj_ver, req_min_ver, req_rel,
                             maj_ver, min_ver, 0)
                        }
                    )
                )

                raise FlowExecutionFailedError(
                    "Detected gluster version: %s"
                    " is lesser than required version: %s" %
                    (
                        NS.tendrl_context.sds_version,
                        reqd_gluster_ver
                    )
                )
            import_gluster(self.parameters)

            if len(node_list) > 1:
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id'],
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={
                            "message": "Waiting for participant nodes %s to be "
                            "imported %s" % (node_list, integration_id)
                        }
                    )
                )
                parent_job = Job(job_id=self.parameters['job_id']).load()
                loop_count = 0
                # Wait for (no of nodes) * 1 minutes for import to complete
                wait_count = (len(node_list) - 1) * 6
                while True:
                    if loop_count >= wait_count:
                        Event(
                            Message(
                                job_id=self.parameters['job_id'],
                                flow_id=self.parameters['flow_id'],
                                priority="info",
                                publisher=NS.publisher_id,
                                payload={
                                    "message": "Import jobs not yet complete "
                                    "on all nodes. Timing out. (%s, %s)" %
                                    (str(node_list), integration_id)
                                }
                            )
                        )
                        return False
                    gevent.sleep(10)
                    finished = True
                    for child_job_id in parent_job.children:
                        child_job = Job(job_id=child_job_id).load()
                        if child_job.status != "finished":
                            finished = False
                            break
                    if not finished:
                        loop_count += 1
                        continue
                    else:
                        break

        except Exception as ex:
            # For traceback
            Event(
                ExceptionMessage(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={
                        "message": ex.message,
                        "exception": ex
                    }
                )
            )
            # raising exception to mark job as failed
            raise ex
        finally:
            # release lock
            create_cluster_utils.release_node_lock(self.parameters)

        return True
