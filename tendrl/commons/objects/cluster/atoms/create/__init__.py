import time

from tendrl.commons.event import Event
from tendrl.commons.flows.create_cluster.ceph_help import create_ceph
from tendrl.commons.flows.create_cluster.gluster_help import create_gluster
from tendrl.commons.flows.create_cluster import utils as create_cluster_utils
from tendrl.commons.message import ExceptionMessage
from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.utils import log_utils as logger


class Create(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(Create, self).__init__(*args, **kwargs)

    def run(self):
        try:
            # Locking nodes
            create_cluster_utils.acquire_node_lock(self.parameters)
            integration_id = self.parameters['TendrlContext.integration_id']
            sds_name = self.parameters["TendrlContext.sds_name"]

            ssh_job_ids = []
            if "ceph" in sds_name:
                ssh_job_ids = create_cluster_utils.ceph_create_ssh_setup_jobs(
                    self.parameters
                )
            else:
                ssh_job_ids = \
                    create_cluster_utils.gluster_create_ssh_setup_jobs(
                        self.parameters
                    )

            while True:
                time.sleep(3)
                all_status = {}
                for job_id in ssh_job_ids:
                    # noinspection PyUnresolvedReferences
                    all_status[job_id] = NS._int.client.read(
                        "/queue/%s/status" % job_id).value

                _failed = {_jid: status for _jid, status in
                           all_status.iteritems() if status == "failed"}
                if _failed:
                    raise AtomExecutionFailedError(
                        "SSH setup failed for jobs %s cluster %s" % (str(
                            _failed), integration_id))
                if all([status == "finished" for status in
                        all_status.values()]):
                    logger.log(
                        "info",
                        NS.publisher_id,
                        {"message": "SSH setup completed for all "
                                    "nodes in cluster %s" %
                                    integration_id},
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id']
                    )
                    # set this node as gluster provisioner
                    if "gluster" in self.parameters["TendrlContext.sds_name"]:
                        tags = ["provisioner/%s" % integration_id]
                        NS.node_context = NS.node_context.load()
                        tags += NS.node_context.tags
                        NS.node_context.tags = list(set(tags))
                        NS.node_context.save()
                    break

            logger.log(
                "info",
                NS.publisher_id,
                {"message": "Starting SDS install and config %s"
                            % integration_id},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )

            # SSH setup jobs finished above, now install sds bits and create
            #  cluster
            if "ceph" in sds_name:
                logger.log(
                    "info",
                    NS.publisher_id,
                    {"message": "Creating Ceph Storage Cluster "
                                "%s" % integration_id},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )

                self.parameters.update({'create_mon_secret': True})
                create_ceph(self.parameters)
            else:
                logger.log(
                    "info",
                    NS.publisher_id,
                    {"message": "Creating Gluster Storage "
                                "Cluster %s" % integration_id},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )

                create_gluster(self.parameters)
        except Exception as ex:
            # For traceback
            Event(
                ExceptionMessage(
                    priority="error",
                    publisher=NS.publisher_id,
                    payload={"message": ex.message,
                             "exception": ex
                             }
                )
            )
            # raising exception to mark job as failed
            raise ex
        finally:
            # releasing nodes if any exception came
            create_cluster_utils.release_node_lock(self.parameters)

        return True
