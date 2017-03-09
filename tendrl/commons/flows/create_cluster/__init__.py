# flake8: noqa

import json
import uuid

from tendrl.commons.objects.job import Job

from tendrl.commons import flows
from tendrl.commons.flows.create_cluster import ceph_help


class CreateCluster(flows.BaseFlow):
    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        NS.tendrl_context.integration_id = integration_id
        NS.tendrl_context.save()
        node_list = self.parameters['Node[]']
        ssh_setup_script = NS.provisioner.get_plugin().setup()
        ssh_job_ids = []
        if len(node_list) > 1:
            for node in node_list:
                if NS.node_context.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                    new_params['ssh_setup_script'] = ssh_setup_script
                # create same flow for each node in node list except $this
                    payload = {"integration_id": integration_id,
                               "node_ids": [node],
                               "run": "tendrl.commons.flows.SetupSsh",
                               "status": "new",
                               "parameters": new_params,
                               "parent": self.parameters['job_id'],
                               "type": "node"
                               }
                    _job_id = str(uuid.uuid4())
                    Job(job_id=_job_id,
                        status="new",
                        payload=json.dumps(payload)).save()
                    ssh_job_ids.append(_job_id)

        all_ssh_jobs_done = False
        while not all_ssh_jobs_done:
            all_status = []
            for job_id in ssh_job_ids:
                all_status.append(NS.etcd_orm.read("/queue/%s/status" %
                                                   job_id).value)
            if all(status == "finished" for status in all_status):
                all_ssh_jobs_done = True

        # SSH setup jobs finished above, now install ceph
        ceph_help.create_ceph(self.parameters)