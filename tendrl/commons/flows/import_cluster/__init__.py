# flake8: noqa

import etcd
import json
import uuid

import etcd
import gevent
from tendrl.commons.objects.job import Job

from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.import_cluster.ceph_help import import_ceph
from tendrl.commons.flows.import_cluster.gluster_help import import_gluster


class ImportCluster(flows.BaseFlow):
    def run(self):

        integration_id = self.parameters['TendrlContext.integration_id']
        if integration_id is None:
            raise FlowExecutionFailedError("TendrlContext.integration_id cannot be empty")

        # Check if nodes participate in some existing cluster
        try:
            clusters = NS.etcd_orm.client.read('clusters')
        except etcd.EtcdKeyNotFound:
            # no clusters imported yet, go ahead
            pass
        else:
            try:
                for entry in self.parameters["Node[]"]:
                    _integration_id = NS.etcd_orm.client.read(
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
                        Event(
                            Message(
                                job_id=self.job_id,
                                flow_id = self.parameters['flow_id'],
                                priority="info",
                                publisher=NS.publisher_id,
                                payload={"message": "Error: Node %s is part of other cluster %s" % (entry, _integration_id.value)
                                     }
                            )
                        )

                        raise FlowExecutionFailedError(
                            "Nodes already participate in existing cluster"
                        )
            except etcd.EtcdKeyNotFound:
                raise FlowExecutionFailedError(
                    "Error while checking pre-participation of nodes in any cluster"
                )
        NS.tendrl_context = NS.tendrl_context.load()
        NS.tendrl_context.integration_id = integration_id
        _detected_cluster = NS.tendrl.objects.DetectedCluster().load()
        NS.tendrl_context.cluster_id = _detected_cluster.detected_cluster_id
        NS.tendrl_context.cluster_name =\
            _detected_cluster.detected_cluster_name
        NS.tendrl_context.sds_name = _detected_cluster.sds_pkg_name
        NS.tendrl_context.sds_version = _detected_cluster.sds_pkg_version
        NS.tendrl_context.save()
        Event(
            Message(
                job_id=self.job_id,
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Registered Node %s with cluster %s" % (NS.node_context.node_id,
                                                                                NS.tendrl_context.integration_id)
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
                        payload=json.dumps(payload)).save()
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


        sds_name = self.parameters['DetectedCluster.sds_pkg_name']
        if "ceph" in sds_name.lower():
            node_context = NS.node_context.load()
            is_mon = False
            for tag in json.loads(node_context.tags):
                mon_tag = NS.compiled_definitions.get_parsed_defs()[
                    'namespace.tendrl'
                ]['tags']['ceph-mon']
                if mon_tag in tag:
                    is_mon = True
            if is_mon:
                # Check if minimum required version of underlying ceph
                # cluster met. If not fail the import task
                detected_cluster = NS.tendrl.objects.DetectedCluster().load()
                maj_ver, min_ver, rel = detected_cluster.sds_pkg_version.split('.')
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
                            priority="info",
                            publisher=NS.publisher_id,
                            payload={"message": "Error: Minimum required version (%s.%s.%s) doesnt match that of detected Ceph Storage (%s.%s.%s)" % (req_maj_ver,
                                                                                                                req_min_ver,
                                                                                                                req_rel,
                                                                                                                maj_ver, min_ver, rel)
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
            maj_ver, min_ver, rel = detected_cluster.sds_pkg_version.split('.')
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
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={"message": "Error: Minimum required version (%s.%s.%s) doesnt match that of detected Gluster Storage (%s.%s.%s)" % (req_maj_ver,
                                                                                                            req_min_ver,
                                                                                                            req_rel,
                                                                                                            maj_ver, min_ver, rel)
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

            
            
        # Wait for all cluster nodes to finish their ImportCluster jobs
        if cluster_nodes:
            all_jobs_done = False
            while not all_jobs_done:
                all_status = []
                for job_id in cluster_nodes:
                    all_status.append(NS.etcd_orm.client.read("/queue/%s/status" %
                                                       job_id).value)
                if all([status for status in all_status if status == "finished"]):
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

                    all_jobs_done = True
                
            
        # import cluster's run() should not return unless the new cluster entry
        # is updated in etcd, as the job is marked as finished if this
        # function is returned. This might lead to inconsistancy in the API
        # functionality. The below loop waits for the cluster details
        # to be updated in etcd.
        while True:
            gevent.sleep(2)
            try:
                NS.etcd_orm.client.read("/clusters/%s" % integration_id)
                break
            except etcd.EtcdKeyNotFound:
                continue
        Event(
            Message(
                job_id=self.parameters['job_id'],
                flow_id = self.parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Cluster successfully imported %s" % integration_id
                     }
            )
        )
