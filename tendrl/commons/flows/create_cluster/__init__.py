# flake8: noqa

import json
import uuid

from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.flows import utils
from tendrl.commons.flows.create_cluster import ceph_help
from tendrl.commons.flows.create_cluster import gluster_help
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.import_cluster.ceph_help import import_ceph
from tendrl.commons.flows.import_cluster.gluster_help import import_gluster
from tendrl.commons.objects.job import Job


class CreateCluster(flows.BaseFlow):
    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        if integration_id is None:
            raise FlowExecutionFailedError("TendrlContext.integration_id cannot be empty")
        supported_sds = NS.compiled_definitions.get_parsed_defs()['namespace.tendrl']['supported_sds']
        sds_name = self.parameters["TendrlContext.sds_name"]
        if sds_name not in supported_sds:
            raise FlowExecutionFailedError("SDS (%s) not supported" % sds_name)
        ssh_job_ids = []
        if "ceph" in sds_name:
            ssh_job_ids = utils.ceph_create_ssh_setup_jobs(self.parameters)
        else:
            ssh_job_ids = utils.gluster_create_ssh_setup_jobs(self.parameters)

        all_ssh_jobs_done = False
        while not all_ssh_jobs_done:
            all_status = []
            for job_id in ssh_job_ids:
                all_status.append(NS.etcd_orm.client.read("/queue/%s/status" %
                                                   job_id).value)
            if all([status for status in all_status if status == "finished"]):
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id = self.parameters['flow_id'],
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={"message": "SSH setup completed for all nodes in cluster %s" % integration_id
                             }
                    )
                )

                all_ssh_jobs_done = True

        # SSH setup jobs finished above, now install sds bits and create cluster
        if "ceph" in sds_name:
            Event(
                Message(
                    job_id=self.parameters['job_id'],
                    flow_id = self.parameters['flow_id'],
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={"message": "Creating Ceph Storage Cluster %s" % integration_id
                         }
                )
            )

            ceph_help.create_ceph(self.parameters)
        else:
            Event(
                Message(
                    job_id=self.parameters['job_id'],
                    flow_id = self.parameters['flow_id'],
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={"message": "Creating Gluster Storage Cluster %s" % integration_id
                         }
                )
            )

            gluster_help.create_gluster(self.parameters)


        # Wait till detected cluster in populated for nodes
        all_nodes_have_detected_cluster = False
        while not all_nodes_have_detected_cluster:
            all_status = []
            for node in self.parameters['Node[]']:
                try:
                    NS.etcd_orm.client.read("/nodes/%s/DetectedCluster" % node)
                    all_status.append(True)
                except etcd.EtcdKeyNotFound:
                    all_status.append(False)
            if all([status for status in all_status if status]):
                all_nodes_have_detected_cluster = True

        # Create the params list for import cluster flow
        new_params = {}
        new_params['Node[]'] = self.parameters['Node[]']
        new_params['TendrlContext.integration_id'] = integration_id

        # Get node context for one of the nodes from list
        sds_pkg_name = NS.etcd_orm.client.read(
            "nodes/%s/DetectedCluster/sds_pkg_name" % self.parameters['Node[]'][0]
        ).value
        sds_pkg_version = NS.etcd_orm.client.read(
            "nodes/%s/DetectedCluster/sds_pkg_version" % self.parameters['Node[]'][0]
        ).value
        new_params['DetectedCluster.sds_pkg_name'] = \
            sds_pkg_name
        new_params['DetectedCluster.sds_pkg_version'] = \
            sds_pkg_version
        payload = {"node_ids": self.parameters['Node[]'],
                   "run": "tendrl.flows.ImportCluster",
                   "status": "new",
                   "parameters": new_params,
                   "parent": self.parameters['job_id'],
                   "type": "node"
                  }
        _job_id = str(uuid.uuid4())
        Job(job_id=_job_id,
            status="new",
            payload=json.dumps(payload)).save()
        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Importing (job_id: %s) newly created %s Storage Cluster %s" % (_job_id,
                                                                                                   sds_pkg_name,
                                                                                       integration_id)
                     }
            )
        )

