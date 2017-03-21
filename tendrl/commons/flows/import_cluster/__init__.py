# flake8: noqa

import etcd
import json
import uuid

import etcd
import gevent
from tendrl.commons.objects.job import Job

from tendrl.commons import flows
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.import_cluster.ceph_help import import_ceph
from tendrl.commons.flows.import_cluster.gluster_help import import_gluster


class ImportCluster(flows.BaseFlow):
    def run(self):

        integration_id = self.parameters['TendrlContext.integration_id']

        # Check if cluster with given id already exists in central store
        try:
            cluster = NS.etcd_orm.client.read(
                'clusters/%s' % self.parameters['TendrlContext.integration_id']
            )
        except etcd.EtcdKeyNotFound:
            # cluster doesnt exist, go ahead and import
            pass
        else:
            raise FlowExecutionFailedError(
                "Cluster with id %s already exists" % integration_id
            )

        # Check if nodes participate in some existing cluster
        try:
            clusters = NS.etcd_orm.client.read('clusters')
        except etcd.EtcdKeyNotFound:
            # no clusters imported yet, go ahead
            pass
        else:
            try:
                for entry in self.parameters["Node[]"]:
                    integration_id = NS.etcd_orm.client.read(
                        'nodes/%s/TendrlContext/integration_id' % entry
                    )
                    if integration_id.value != "":
                        raise FlowExecutionFailedError(
                            "Nodes already participate in existing cluster"
                        )
            except etcd.EtcdKeyNotFound:
                raise FlowExecutionFailedError(
                    "Error while checking pre-participation of nodes in any cluster"
                )

        NS.tendrl_context.integration_id = integration_id
        NS.tendrl_context.save()
        node_list = self.parameters['Node[]']
        if len(node_list) > 1:
            # This is the master node for this flow
            for node in node_list:
                if NS.node_context.node_id != node:
                    new_params = self.parameters.copy()
                    new_params['Node[]'] = [node]
                    # create same flow for each node in node list except $this
                    payload = {"integration_id": integration_id,
                               "node_ids": [node],
                               "run": "tendrl.flows.ImportCluster",
                               "status": "new",
                               "parameters": new_params,
                               "parent": self.parameters['job_id'],
                               "type": "node"
                               }

                    Job(job_id=str(uuid.uuid4()),
                        status="new",
                        payload=json.dumps(payload)).save()

        sds_name = self.parameters['DetectedCluster.sds_pkg_name']
        if "ceph" in sds_name.lower():
            node_context = NS.node_context.load()
            is_mon = False
            for tag in json.loads(node_context.tags):
                if "ceph/mon" in tag:
                    is_mon = True
            if is_mon:
                import_ceph(NS.tendrl_context.integration_id)
        else:
            # Check if minimum required version of underlying gluster
            # cluster met. If not fail the import task
            detected_cluster = NS.tendrl.objects.DetectedCluster().load()
            maj_ver, min_ver, rel = detected_cluster.sds_pkg_version.split('.')
            reqd_gluster_ver = NS.compiled_definitions.get_parsed_defs()[
                'namespace.tendrl'
            ]['min_reqd_gluster_ver']
            req_maj_ver, req_min_ver, req_rel = reqd_gluster_ver.split('.')
            if int(maj_ver) < int(req_maj_ver) or \
                int(min_ver) < int(req_min_ver):
                raise FlowExecutionFailedError(
                    "Detected gluster version: %s"
                    " is lesser than required version: %s" %
                    (
                        detected_cluster.sds_pkg_version,
                        reqd_gluster_ver
                    )
                )
            import_gluster(NS.tendrl_context.integration_id)

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
