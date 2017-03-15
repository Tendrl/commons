# flake8: noqa

import uuid

from tendrl.commons import flows
from tendrl.commons.flows import utils
from tendrl.commons.flows.create_cluster import ceph_help
from tendrl.commons.flows.create_cluster import gluster_help


class CreateCluster(flows.BaseFlow):
    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        NS.tendrl_context.integration_id = integration_id
        NS.tendrl_context.save()
        ssh_job_ids = []
        if self.parameters['sds_type'] == "ceph":
            ssh_job_ids = utils.ceph_setup_ssh(self.parameters)
        else:
            ssh_job_ids = utils.gluster_setup_ssh(self.parameters)

        all_ssh_jobs_done = False
        while not all_ssh_jobs_done:
            all_status = []
            for job_id in ssh_job_ids:
                all_status.append(NS.etcd_orm.client.read("/queue/%s/status" %
                                                   job_id).value)
            if all(status == "finished" for status in all_status):
                all_ssh_jobs_done = True

        # SSH setup jobs finished above, now install sds bits and create cluster
        if self.parameters['sds_type'] == "ceph":
            ceph_help.create_ceph(self.parameters)
        else:
            gluster_help.create_gluster(self.parameters)

    def load_definition(self):
        return {"help": "Create Cluster",
                "uuid": "dc4c8775-1595-43c7-a6c6-517f0084498f"}
