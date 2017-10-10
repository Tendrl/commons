import time
import uuid


import etcd


from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons import objects
from tendrl.commons.objects.job import Job


class ImportCreatedCluster(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(ImportCreatedCluster, self).__init__(*args, **kwargs)

    def run(self):
        integration_id = self.parameters['TendrlContext.integration_id']
        # Wait till detected cluster in populated for nodes
        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "SDS install and config completed, "
                               "Waiting for tendrl-node-agent to "
                               "detect newly installed sds details %s %s" % (
                                   integration_id,
                                   self.parameters['Node[]']
                               )
                }
            )
        )

        while True:
            time.sleep(3)
            all_status = []
            for node in self.parameters['Node[]']:
                try:
                    NS._int.client.read(
                        "/nodes/%s/DetectedCluster/detected_cluster_id" %
                        node
                    )
                    all_status.append(True)
                except etcd.EtcdKeyNotFound:
                    all_status.append(False)
            if all_status:
                if all(all_status):
                    break

        # Create the params list for import cluster flow
        new_params = dict()
        new_params['Node[]'] = self.parameters['Node[]']
        new_params['TendrlContext.integration_id'] = integration_id

        # Get node context for one of the nodes from list
        detected_cluster_id = NS._int.client.read(
            "nodes/%s/DetectedCluster/detected_cluster_id" %
            self.parameters['Node[]'][0]
        ).value
        sds_pkg_name = NS._int.client.read(
            "nodes/%s/DetectedCluster/sds_pkg_name" % self.parameters['Node['
                                                                      ']'][0]
        ).value
        sds_pkg_version = NS._int.client.read(
            "nodes/%s/DetectedCluster/sds_pkg_version" % self.parameters[
                'Node[]'][0]
        ).value
        new_params['DetectedCluster.sds_pkg_name'] = \
            sds_pkg_name
        new_params['DetectedCluster.sds_pkg_version'] = \
            sds_pkg_version
        new_params['import_after_create'] = True
        payload = {"tags": ["detected_cluster/%s" % detected_cluster_id],
                   "run": "tendrl.flows.ImportCluster",
                   "status": "new",
                   "parameters": new_params,
                   "parent": self.parameters['job_id'],
                   "type": "node"
                   }
        _job_id = str(uuid.uuid4())

        Job(job_id=_job_id,
            status="new",
            payload=payload).save()
        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Please wait while Tendrl imports newly "
                                    "created %s SDS Cluster %s"
                         " Import job id :%s" % (sds_pkg_name, integration_id,
                                                 _job_id)
                         }
            )
        )

        return True
