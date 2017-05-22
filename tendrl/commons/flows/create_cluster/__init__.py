import uuid

import etcd
import gevent

from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.flows.create_cluster import ceph_help
from tendrl.commons.flows.create_cluster import gluster_help
from tendrl.commons.flows.create_cluster import utils as create_cluster_utils
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
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
        
        # Check if clusre name contains space char and fail if so
        if ' ' in self.parameters['TendrlContext.cluster_name']:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={
                        "message": "Space char not allowed in cluster name"
                    },
                    job_id=self.job_id,
                    flow_id=self.parameters['flow_id'],
                    cluster_id=NS.tendrl_context.integration_id,
                )
            )
            raise FlowExecutionFailedError(
                "Space char not allowed in cluster name"
            )

        ssh_job_ids = []
        if "ceph" in sds_name:
            ssh_job_ids = create_cluster_utils.ceph_create_ssh_setup_jobs(
                self.parameters
            )
        else:
            create_cluster_utils.install_gdeploy()
            create_cluster_utils.install_python_gdeploy()
            ssh_job_ids = create_cluster_utils.gluster_create_ssh_setup_jobs(
                self.parameters
            )

        while True:
            gevent.sleep(3)
            all_status = {}
            for job_id in ssh_job_ids:
                # noinspection PyUnresolvedReferences
                all_status[job_id] = NS._int.client.read("/queue/%s/status" % job_id).value
            
            _failed = {_jid: status for _jid, status in all_status.iteritems() if status == "failed"}
            if _failed:
                raise FlowExecutionFailedError("SSH setup failed for jobs %s cluster %s" % (str(_failed),
                                                                                           integration_id))
            if all([status == "finished" for status in all_status.values()]):
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
                    # set this node as gluster provisioner
                if "gluster" in self.parameters["TendrlContext.sds_name"]:
                    tags = ["provisioner/%s" % integration_id]
                    NS.node_context = NS.node_context.load()
                    tags += NS.node_context.tags
                    NS.node_context.tags = list(set(tags))
                    NS.node_context.save()
                break

                                               
        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Starting SDS install and config %s" % integration_id
                     }
            )
        )

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

            self.parameters.update({'create_mon_secret': True})
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
        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "SDS install and config completed, "
                                    "checking following nodes for"
                                    "detected sds details %s %s" % (integration_id,
                                                                    self.parameters['Node[]'])
                     }
            )
        )

        while True:
            gevent.sleep(3)
            all_status = []
            for node in self.parameters['Node[]']:
                try:
                    NS._int.client.read("/nodes/%s/DetectedCluster/detected_cluster_id" %
                                        node)
                    all_status.append(True)
                except etcd.EtcdKeyNotFound:
                    all_status.append(False)
            if all_status:
                if all(all_status):
                    break

        # Create the params list for import cluster flow
        new_params = {}
        new_params['Node[]'] = self.parameters['Node[]']
        new_params['TendrlContext.integration_id'] = integration_id

        # Get node context for one of the nodes from list
        detected_cluster_id = NS._int.client.read(
            "nodes/%s/DetectedCluster/detected_cluster_id" % self.parameters['Node[]'][0]
        ).value
        sds_pkg_name = NS._int.client.read(
            "nodes/%s/DetectedCluster/sds_pkg_name" % self.parameters['Node[]'][0]
        ).value
        if "gluster" in sds_pkg_name:
            new_params['gdeploy_provisioned'] = True
        sds_pkg_version = NS._int.client.read(
            "nodes/%s/DetectedCluster/sds_pkg_version" % self.parameters['Node[]'][0]
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
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Importing (job_id: %s) newly created %s Storage Cluster %s" % (_job_id,
                                                                                                   sds_pkg_name,
                                                                                       integration_id)
                     }
            )
        )
