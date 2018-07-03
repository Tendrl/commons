import subprocess
import time
import uuid

from tendrl.commons.event import Event
from tendrl.commons.flows.import_cluster.gluster_help import import_gluster
from tendrl.commons.flows import utils as flow_utils
from tendrl.commons.message import ExceptionMessage
from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.utils import log_utils as logger


class ImportCluster(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(ImportCluster, self).__init__(*args, **kwargs)

    def run(self):
        try:
            integration_id = self.parameters['TendrlContext.integration_id']
            _cluster = NS.tendrl.objects.Cluster(
                integration_id=integration_id
            ).load()

            # Lock nodes
            flow_utils.acquire_node_lock(self.parameters)
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
                        NS.tendrl.objects.Job(
                            job_id=_job_id,
                            status="new",
                            payload=payload
                        ).save()
                        logger.log(
                            "info",
                            NS.publisher_id,
                            {"message": "ImportCluster %s (jobID: %s) :"
                                        "importing host %s" %
                             (_cluster.short_name, _job_id, node)},
                            job_id=self.parameters['job_id'],
                            flow_id=self.parameters['flow_id']
                        )
            # Check if minimum required version of underlying gluster
            # cluster met. If not fail the import task
            # A sample output from "rpm -qa | grep glusterfs-server"
            # looks as below
            # `glusterfs-server-3.8.4-54.4.el7rhgs.x86_64`
            # In case of upstream build the format could be as below
            # `glusterfs-server-4.1dev-0.203.gitc3e1a2e.el7.centos.x86_64`
            # `glusterfs-server-3.12.8-0.0.el7.centos.x86_64.rpm`
            cmd = subprocess.Popen(
                'rpm -q glusterfs-server',
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            out, err = cmd.communicate()
            if out in [None, ""] or err:
                raise AtomExecutionFailedError(
                    "Failed to detect underlying cluster version"
                )
            lines = out.split('\n')
            build_no = None
            req_build_no = None
            ver_det = lines[0].split('glusterfs-server-')[-1].split('.')
            maj_ver = ver_det[0]
            min_ver = ver_det[1]
            if 'dev' in min_ver:
                min_ver = min_ver[0]
            rel = ver_det[2]
            if '-' in rel:
                build_no = rel.split('-')[-1]
                rel = rel.split('-')[0]
            reqd_gluster_ver = NS.compiled_definitions.get_parsed_defs()[
                'namespace.tendrl'
            ]['min_reqd_gluster_ver']
            req_maj_ver, req_min_ver, req_rel = reqd_gluster_ver.split('.')
            if '-' in req_rel:
                req_build_no = req_rel.split('-')[-1]
                req_rel = req_rel.split('-')[0]
            logger.log(
                "info",
                NS.publisher_id,
                {"message": "Checking minimum required version ("
                            "%s.%s.%s) of Gluster Storage" %
                 (req_maj_ver, req_min_ver, req_rel)},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            ver_check_failed = False
            if int(maj_ver) < int(req_maj_ver):
                ver_check_failed = True
            else:
                if int(maj_ver) == int(req_maj_ver):
                    if int(min_ver) < int(req_min_ver):
                        ver_check_failed = True
                    else:
                        if int(min_ver) == int(req_min_ver):
                            if int(rel) < int(req_rel):
                                ver_check_failed = True
                            else:
                                if int(rel) == int(req_rel):
                                    if build_no is not None and \
                                        req_build_no is not None and \
                                        int(build_no) < int(req_build_no):
                                        ver_check_failed = True
            if ver_check_failed:
                logger.log(
                    "error",
                    NS.publisher_id,
                    {"message": "Error: Minimum required version "
                                "(%s.%s.%s) "
                     "doesnt match that of detected Gluster "
                                "Storage (%s.%s.%s)" %
                     (req_maj_ver, req_min_ver, req_rel,
                      maj_ver, min_ver, 0)},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )

                raise AtomExecutionFailedError(
                    "Detected gluster version: %s"
                    " is lesser than required version: %s" %
                    (
                        NS.tendrl_context.sds_version,
                        reqd_gluster_ver
                    )
                )
            ret_val, err = import_gluster(self.parameters)
            if not ret_val:
                raise AtomExecutionFailedError(
                    "Error importing the cluster (integration_id: %s). "
                    "Error: %s" % (integration_id, err)
                )

            if len(node_list) > 1:
                logger.log(
                    "info",
                    NS.publisher_id,
                    {"message": "ImportCluster %s waiting for hosts %s "
                        "to be imported" % (_cluster.short_name, node_list)},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                loop_count = 0
                # Wait for (no of nodes) * 6 minutes for import to complete
                wait_count = (len(node_list) - 1) * 36
                while True:
                    child_jobs_failed = []
                    parent_job = NS.tendrl.objects.Job(
                        job_id=self.parameters['job_id']
                    ).load()
                    if loop_count >= wait_count:
                        logger.log(
                            "info",
                            NS.publisher_id,
                            {"message": "Import jobs on cluster(%s) not yet "
                             "complete on all nodes(%s). Timing out." %
                             (_cluster.short_name, str(node_list))},
                            job_id=self.parameters['job_id'],
                            flow_id=self.parameters['flow_id']
                        )
                        return False
                    time.sleep(10)
                    completed = True
                    for child_job_id in parent_job.children:
                        child_job = NS.tendrl.objects.Job(
                            job_id=child_job_id
                        ).load()
                        if child_job.status not in ["finished", "failed"]:
                            completed = False
                        elif child_job.status == "failed":
                            child_jobs_failed.append(child_job.job_id)
                    if completed:
                        break
                    else:
                        loop_count += 1
                        continue
                if len(child_jobs_failed) > 0:
                    _msg = "Child jobs failed %s" % child_jobs_failed
                    logger.log(
                        "error",
                        NS.publisher_id,
                        {"message": _msg},
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
                    return False
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
            flow_utils.release_node_lock(self.parameters)

        return True
