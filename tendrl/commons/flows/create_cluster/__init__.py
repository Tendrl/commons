# flake8: noqa

import json
import uuid

from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.flows import utils
from tendrl.commons.flows.create_cluster import ceph_help
from tendrl.commons.flows.create_cluster import gluster_help
from tendrl.commons.flows.import_cluster.ceph_help import import_ceph
from tendrl.commons.flows.import_cluster.gluster_help import import_gluster
from tendrl.commons.objects.job import Job


class CreateCluster(flows.BaseFlow):
    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        NS.tendrl_context = NS.tendrl_context.load()
        NS.tendrl_context.integration_id = integration_id
        NS.tendrl_context.save()
        ssh_job_ids = []
        if "ceph" in self.parameters["TendrlContext.sds_name"]:
            ssh_job_ids = utils.ceph_create_ssh_setup_jobs(self.parameters)
        else:
            ssh_job_ids = utils.gluster_create_ssh_setup_jobs(self.parameters)

        all_ssh_jobs_done = False
        while not all_ssh_jobs_done:
            all_status = []
            for job_id in ssh_job_ids:
                all_status.append(NS.etcd_orm.client.read("/queue/%s/status" %
                                                   job_id).value)
            if all(status == "finished" for status in all_status):
                all_ssh_jobs_done = True

        # SSH setup jobs finished above, now install sds bits and create cluster
        if "ceph" in self.parameters["TendrlContext.sds_name"]:
            ceph_help.create_ceph(self.parameters)
        else:
            gluster_help.create_gluster(self.parameters)

        # Start jobs for importing cluster
        node_list = self.parameters['Node[]']
        try:
            node_list.remove(NS.node_context.node_id)
        except ValueError:
            # key not found. ignore
            pass
        new_params = self.parameters.copy()
        new_params['Node[]'] = node_list
        # Get node context for one of the nodes from list
        sds_pkg_name = NS.etcd_orm.client.read(
            "nodes/%s/DetectedCluster/sds_pkg_name" % node_list[0]
        ).value
        sds_pkg_version = NS.etcd_orm.client.read(
            "nodes/%s/DetectedCluster/sds_pkg_version" % node_list[0]
        ).value
        new_params['DetectedCluster.sds_pkg_name'] = \
            sds_pkg_name
        new_params['DetectedCluster.sds_pkg_version'] = \
            sds_pkg_version
        payload = {"node_ids": node_list,
                   "run": "tendrl.flows.ImportCluster",
                   "status": "new",
                   "parameters": new_params,
                   "parent": self.parameters['job_id'],
                   "type": "node"
                  }
        Job(job_id=str(uuid.uuid4()),
            status="new",
            payload=json.dumps(payload)).save()
