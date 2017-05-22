import uuid

import etcd
import gevent

from tendrl.commons.objects.job import Job
from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.flows.create_cluster import utils as create_cluster_utils
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.import_cluster.ceph_help import import_ceph
from tendrl.commons.flows.import_cluster.gluster_help import import_gluster
from tendrl.commons.message import Message


class ImportCluster(flows.BaseFlow):
    def run(self):

        integration_id = self.parameters['TendrlContext.integration_id']
        if integration_id is None:
            raise FlowExecutionFailedError("TendrlContext.integration_id cannot be empty")
        sds_name = self.parameters['DetectedCluster.sds_pkg_name']

        if not self.parameters.get('import_after_expand', False) and \
            not self.parameters.get('import_after_create', False):
            # Above condition means, this is a fresh import
            # Check if nodes participate in some existing cluster
            try:
                for entry in self.parameters["Node[]"]:
                    _integration_id = NS._int.client.read(
                        'nodes/%s/TendrlContext/integration_id' % entry
                    )
                    Event(
                        Message(
                            job_id=self.job_id,
                            flow_id = self.parameters['flow_id'],
                            priority="info",
                            publisher=NS.publisher_id,
                            payload={
                                "message": "Check: Node %s not part of any other cluster" % entry
                            }
                        )
                    )

                    if _integration_id.value != "":
                        _msg = "Error: Node %s is already part of other " \
                               "cluster %s" % (entry, _integration_id.value)
                        Event(
                            Message(
                                job_id=self.job_id,
                                flow_id = self.parameters['flow_id'],
                                priority="error",
                                publisher=NS.publisher_id,
                                payload={"message": _msg
                                     }
                            )
                        )

                        raise FlowExecutionFailedError(_msg)
            except etcd.EtcdKeyNotFound:
                raise FlowExecutionFailedError(
                    "Error while checking pre-participation of nodes in any cluster"
                )

            # check if gdeploy in already provisioned in this cluster
            # if no it has to be provisioned here
            if not self.parameters.get('gdeploy_provisioned', False) and sds_name.find("gluster") > -1:
                create_cluster_utils.install_gdeploy()
                create_cluster_utils.install_python_gdeploy()
                ssh_job_ids = create_cluster_utils.gluster_create_ssh_setup_jobs(
                    self.parameters
                )

                while True:
                    gevent.sleep(3)
                    all_status = {}
                    for job_id in ssh_job_ids:
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
                        tags = ["provisioner/%s" % integration_id]
                        NS.node_context = NS.node_context.load()
                        tags += NS.node_context.tags
                        NS.node_context.tags = list(set(tags))
                        NS.node_context.save()

                        # set gdeploy_provisioned to true so that no other nodes
                        # tries to configure gdeploy
                        self.parameters['gdeploy_provisioned'] = True
                        break

        NS.tendrl_context = NS.tendrl_context.load()
        NS.tendrl_context.integration_id = integration_id
        _detected_cluster = NS.tendrl.objects.DetectedCluster().load()
        NS.tendrl_context.cluster_id = _detected_cluster.detected_cluster_id
        NS.tendrl_context.cluster_name = _detected_cluster.detected_cluster_name
        NS.tendrl_context.sds_name = _detected_cluster.sds_pkg_name
        NS.tendrl_context.sds_version = _detected_cluster.sds_pkg_version
        NS.tendrl_context.save()
        Event(
            Message(
                job_id=self.job_id,
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Registered Node %s with cluster %s" % (
                        NS.node_context.node_id,
                        NS.tendrl_context.integration_id
                    )
                }
            )
        )

        node_list = self.parameters['Node[]']
        cluster_nodes = []
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if NS.node_context.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                    # create same flow for each node in node list except $this
                    payload = {"node_ids": [node],
                               "run": "tendrl.flows.ImportCluster",
                               "status": "new",
                               "parameters": new_params,
                               "parent": self.job_id,
                               "type": "node"
                               }
                    _job_id = str(uuid.uuid4())
                    cluster_nodes.append(_job_id)
                    Job(job_id=_job_id,
                        status="new",
                        payload=payload).save()
                    Event(
                        Message(
                            job_id=self.job_id,
                            flow_id = self.parameters['flow_id'],
                            priority="info",
                            publisher=NS.publisher_id,
                            payload={"message": "Importing (job: %s) Node %s to cluster %s" % (_job_id, node, integration_id)
                                 }
                        )
                    )


        if "ceph" in sds_name.lower():
            node_context = NS.node_context.load()
            is_mon = False
            for tag in node_context.tags:
                mon_tag = NS.compiled_definitions.get_parsed_defs()[
                    'namespace.tendrl'
                ]['tags']['ceph-mon']
                if mon_tag in tag:
                    is_mon = True
            if is_mon:
                # Check if minimum required version of underlying ceph
                # cluster met. If not fail the import task
                detected_cluster = NS.tendrl.objects.DetectedCluster().load()
                detected_cluster_ver = detected_cluster.sds_pkg_version.split('.')
                maj_ver = detected_cluster_ver[0]
                min_ver = detected_cluster_ver[1]
                reqd_ceph_ver = NS.compiled_definitions.get_parsed_defs()[
                    'namespace.tendrl'
                ]['min_reqd_ceph_ver']
                req_maj_ver, req_min_ver, req_rel = reqd_ceph_ver.split('.')
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id = self.parameters['flow_id'],
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={"message": "Check: Minimum required version (%s.%s.%s) of Ceph Storage" % (req_maj_ver,
                                                                                                            req_min_ver,
                                                                                                            req_rel)
                             }
                    )
                )

                if int(maj_ver) < int(req_maj_ver) or \
                    int(min_ver) < int(req_min_ver):
                    Event(
                        Message(
                            job_id=self.parameters['job_id'],
                            flow_id = self.parameters['flow_id'],
                            priority="error",
                            publisher=NS.publisher_id,
                            payload={"message": "Error: Minimum required version (%s.%s.%s) doesnt match that of detected Ceph Storage (%s.%s.%s)" % (req_maj_ver,
                                                                                                                req_min_ver,
                                                                                                                req_rel,
                                                                                                                maj_ver, min_ver, 0)
                                 }
                        )
                    )

                    raise FlowExecutionFailedError(
                        "Detected ceph version: %s"
                        " is lesser than required version: %s" %
                        (
                            detected_cluster.sds_pkg_version,
                            reqd_ceph_ver
                        )
                    )
                import_ceph(self.parameters)
        else:
            # Check if minimum required version of underlying gluster
            # cluster met. If not fail the import task
            detected_cluster = NS.tendrl.objects.DetectedCluster().load()
            detected_cluster_ver = detected_cluster.sds_pkg_version.split('.')
            maj_ver = detected_cluster_ver[0]
            min_ver = detected_cluster_ver[1]
            reqd_gluster_ver = NS.compiled_definitions.get_parsed_defs()[
                'namespace.tendrl'
            ]['min_reqd_gluster_ver']
            req_maj_ver, req_min_ver, req_rel = reqd_gluster_ver.split('.')
            Event(
                Message(
                    job_id=self.parameters['job_id'],
                    flow_id = self.parameters['flow_id'],
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={"message": "Check: Minimum required version (%s.%s.%s) of Gluster Storage" % (req_maj_ver,
                                                                                                        req_min_ver,
                                                                                                        req_rel)
                         }
                )
            )

            if int(maj_ver) < int(req_maj_ver) or \
                int(min_ver) < int(req_min_ver):
                Event(
                    Message(
                        job_id=self.parameters['job_id'],
                        flow_id = self.parameters['flow_id'],
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "Error: Minimum required version (%s.%s.%s) doesnt match that of detected Gluster Storage (%s.%s.%s)" % (req_maj_ver,
                                                                                                            req_min_ver,
                                                                                                            req_rel,
                                                                                                            maj_ver, min_ver, 0)
                             }
                    )
                )

                raise FlowExecutionFailedError(
                    "Detected gluster version: %s"
                    " is lesser than required version: %s" %
                    (
                        detected_cluster.sds_pkg_version,
                        reqd_gluster_ver
                    )
                )
            import_gluster(self.parameters)

        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Waiting for participant nodes %s to be "
                                    "imported %s" % (node_list, integration_id)
                     }
            )
        )

        # An import is sucessfull once all Node[] register to /clusters/:integration_id/nodes/:node_id
        while True:
            _all_node_status = []
            gevent.sleep(3)
            for node_id in self.parameters['Node[]']:
                _status = NS.tendrl.objects.ClusterNodeContext(node_id=node_id).exists() and NS.tendrl.objects.ClusterTendrlContext(integration_id=integration_id).exists()
                _all_node_status.append(_status)
            if _all_node_status:
                if all(_all_node_status):
                    Event(
                        Message(
                            job_id=self.parameters['job_id'],
                            flow_id = self.parameters['flow_id'],
                            priority="info",
                            publisher=NS.publisher_id,
                            payload={"message": "Import Cluster completed for all nodes in cluster %s" % integration_id
                                 }
                        )
                    )

                    break


        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Sucessfully imported cluster %s" % integration_id
                     }
            )
        )
