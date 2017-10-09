import etcd

import time
import uuid

from tendrl.commons.event import Event
from tendrl.commons import flows
from tendrl.commons.flows.create_cluster import \
    utils as create_cluster_utils
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.expand_cluster import ceph_help
from tendrl.commons.flows.expand_cluster import gluster_help
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.message import Message
from tendrl.commons.objects.job import Job


class ExpandCluster(flows.BaseFlow):
    def run(self):
        try:
            # Lock nodes
            create_cluster_utils.acquire_node_lock(self.parameters)
            integration_id = self.parameters['TendrlContext.integration_id']
            if integration_id is None:
                raise FlowExecutionFailedError(
                    "TendrlContext.integration_id cannot be empty"
                )

            supported_sds = NS.compiled_definitions.get_parsed_defs()[
                'namespace.tendrl']['supported_sds']
            sds_name = self.parameters["TendrlContext.sds_name"]
            if sds_name not in supported_sds:
                raise FlowExecutionFailedError("SDS (%s) not supported" %
                                               sds_name)

            ssh_job_ids = []
            if "ceph" in sds_name:
                ssh_job_ids = create_cluster_utils.ceph_create_ssh_setup_jobs(
                    self.parameters
                )
            else:
                ssh_job_ids = \
                    create_cluster_utils.gluster_create_ssh_setup_jobs(
                        self.parameters,
                        skip_current_node=True
                    )

            while True:
                time.sleep(3)
                all_status = {}
                for job_id in ssh_job_ids:
                    all_status[job_id] = NS._int.client.read(
                        "/queue/%s/status" % job_id).value

                _failed = {_jid: status for _jid, status in
                           all_status.iteritems() if status == "failed"}
                if _failed:
                    raise FlowExecutionFailedError(
                        "SSH setup failed for jobs %s cluster %s" % (str(
                            _failed), integration_id))
                if all([status == "finished" for status in
                        all_status.values()]):
                    Event(
                        Message(
                            job_id=self.parameters['job_id'],
                            flow_id=self.parameters['flow_id'],
                            priority="info",
                            publisher=NS.publisher_id,
                            payload={
                                "message": "SSH setup completed for all "
                                "nodes in cluster %s" % integration_id
                            }
                        )
                    )

                    break

            # SSH setup jobs finished above, now install sds
            # bits and create cluster
            if "ceph" in sds_name:
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id'],
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={
                            "message": "Expanding ceph cluster %s" %
                                       integration_id
                        }
                    )
                )
                ceph_help.expand_cluster(self.parameters)
            else:
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id=self.parameters['flow_id'],
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={
                            "message": "Expanding Gluster Storage"
                            " Cluster %s" % integration_id
                        }
                    )
                )
                gluster_help.expand_gluster(self.parameters)
            Event(
                Message(
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id'],
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "SDS install/config completed on newly "
                        "expanded nodes, Please wait while "
                        "tendrl-node-agents detect sds details on the newly "
                        "expanded nodes %s" % self.parameters['Node[]']
                    }
                )
            )

            # Wait till detected cluster in populated for nodes
            while True:
                time.sleep(3)
                all_status = []
                detected_cluster = ""
                different_cluster_id = False
                dc = ""
                for node in self.parameters['Node[]']:
                    try:
                        dc = NS._int.client.read(
                            "/nodes/%s/DetectedCluster/detected_cluster_id"
                            % node
                        ).value
                        if not detected_cluster:
                            detected_cluster = dc
                        else:
                            if detected_cluster != dc:
                                all_status.append(False)
                                different_cluster_id = True
                                break
                        all_status.append(True)
                    except etcd.EtcdKeyNotFound:
                        all_status.append(False)
                if different_cluster_id:
                    raise FlowExecutionFailedError(
                        "Seeing different detected cluster id in"
                        " different nodes. %s and %s" % (
                            detected_cluster, dc)
                    )

                if all_status:
                    if all(all_status):
                        break

            # Create the params list for import cluster flow
            new_params = dict()
            new_params['Node[]'] = self.parameters['Node[]']
            new_params['TendrlContext.integration_id'] = integration_id

            # Get node context for one of the nodes from list
            sds_pkg_name = NS._int.client.read(
                "nodes/%s/DetectedCluster/"
                "sds_pkg_name" % self.parameters['Node[]'][0]
            ).value
            new_params['import_after_expand'] = True
            sds_pkg_version = NS._int.client.read(
                "nodes/%s/DetectedCluster/sds_pkg_"
                "version" % self.parameters['Node[]'][0]
            ).value
            new_params['DetectedCluster.sds_pkg_name'] = \
                sds_pkg_name
            new_params['DetectedCluster.sds_pkg_version'] = \
                sds_pkg_version

            tags = []
            for node in self.parameters['Node[]']:
                tags.append("tendrl/node_%s" % node)
            payload = {
                "tags": tags,
                "run": "tendrl.flows.ImportCluster",
                "status": "new",
                "parameters": new_params,
                "parent": self.parameters['job_id'],
                "type": "node"
            }
            _job_id = str(uuid.uuid4())
            # release lock before import cluster
            create_cluster_utils.release_node_lock(self.parameters)

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
                        "message": "Please wait while Tendrl imports ("
                                   "job_id: %s) newly expanded "
                        "%s storage nodes %s" % (
                            _job_id,
                            sds_pkg_name,
                            integration_id
                        )
                    }
                )
            )
        except Exception as ex:
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
            # release lock if any exception came
            create_cluster_utils.release_node_lock(self.parameters)
