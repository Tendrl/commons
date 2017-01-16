import json
import logging
import traceback
import uuid

import gevent.event
import yaml

from tendrl.commons.definitions.validator import DefinitionsSchemaValidator
from tendrl.commons.etcdobj.etcdobj import Server as etcd_server
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils import import_utils

LOG = logging.getLogger(__name__)


class EtcdRPC(object):
    def __init__(self, syncjobthread, etcd_client):
        self.config = syncjobthread._manager._config
        self.client = etcd_client
        self.syncJobThread = syncjobthread

    def _process_job(self, raw_job, job_key, job_type):
        # Pick up the "new" job that is not locked by any other integration
        if raw_job['status'] == "new" and raw_job["type"] == job_type:
            raw_job['status'] = "processing"
            # Generate a request ID for tracking this job
            # further by tendrl-api
            req_id = str(uuid.uuid4())
            raw_job['request_id'] = "/clusters/%s/_jobs/%s_%s" % (
                self.syncJobThread._manager.integration_id, raw_job['run'],
                req_id)
            self.client.write(job_key, json.dumps(raw_job))
            try:
                definitions = self.validate_flow(raw_job)
                if definitions:
                    self.invoke_flow(raw_job['run'], raw_job, definitions)
            except FlowExecutionFailedError as e:
                LOG.error(e)
                raw_job['status'] = "failed"
            else:
                raw_job['status'] = "finished"

            return raw_job, True
        else:
            return raw_job, False

    def _acceptor(self, job_type):
        while not self.syncJobThread._complete.is_set():
            jobs = self.client.read("/queue")
            for job in jobs.children:
                executed = False
                if job.value is None:
                    continue
                raw_job = json.loads(job.value.decode('utf-8'))
                try:
                    # If current node's id does not fall under job's node_ids,
                    # ignore the job and dont process
                    if "node_ids" in raw_job:
                        if self.syncJobThread._manager.node_id \
                                not in raw_job['node_ids']:
                            continue
                    raw_job, executed = self._process_job(
                        raw_job,
                        job.key,
                        job_type
                    )
                    if "etcd_server" and "manager" and "config" in \
                            raw_job['parameters'].keys():
                        del raw_job['parameters']['etcd_server']
                        del raw_job['parameters']['manager']
                        del raw_job['parameters']['config']
                except FlowExecutionFailedError as e:
                    LOG.error(e)
                if executed:
                    self.client.write(job.key, json.dumps(raw_job))
                    break
            gevent.sleep(2)

    def run(self):
        self._acceptor(self.syncJobThread._manager.name)

    def stop(self):
        pass

    def validate_flow(self, raw_job):
        definitions = yaml.load(
            self.client.read(
                self.syncJobThread._manager.defs_dir
            ).value.decode("utf-8")
        )
        definitions = DefinitionsSchemaValidator(
            definitions).sanitize_definitions()

        return definitions

    def invoke_flow(self, flow_name, job, definitions):
        atoms, help, enabled, inputs, pre_run, post_run, type, uuid = \
            self.extract_flow_details(flow_name, definitions)
        job['parameters'].update({"manager": self.syncJobThread._manager,
                                  "etcd_server": self.client,
                                  "config": self.config})
        if "tendrl" in flow_name and "flows" in flow_name:
            the_flow = import_utils.load_abs_class(flow_name)
            return the_flow(flow_name, atoms, help, enabled, inputs, pre_run,
                            post_run, type, uuid, job['parameters'],
                            job, self.config, definitions).run()

    def extract_flow_details(self, flow_name, definitions):
        try:
            # This block takes care of extracting the flows that are at the
            # global level. For example:
            # "tendrl.node_agent.ceph_integration.flows.
            # import_cluster.ImportCluster"
            # For above flow the dictionary to extract flow would be
            # definitions["tendrl.node_agent.ceph_integration"]["flows"]
            # ["ImportCluster"]
            namespace = flow_name.split(".flows.")[0]
            flow = definitions[namespace]['flows'][flow_name.split(".")[-1]]
        except KeyError:
            # This section is for extracting flows that are tied to objects
            # For example:
            # "tendrl.gluster_integration.objects.Volume.flows.
            # delete_volume.DeleteVolume"
            # Here the dictionary for extracting flow is
            # definition["tendrl.gluster_integration"]["objects"]["Volume"]
            # ["flows"]["DeleteVolume"]
            # in this case we parse the dictionary step by step
            namespace = flow_name.split(".flows.")[0]
            namespace = namespace.split(".")
            integration_path = namespace[0] + "." + namespace[1]
            flow = definitions[integration_path]
            for path in namespace[2:]:
                flow = flow[path]
            flow = flow['flows']
            flow = flow[flow_name.split(".")[-1]]

        return flow['atoms'], flow.get('help', ""), \
            flow['enabled'], flow['inputs'], \
            flow.get('pre_run'), flow.get('post_run'), \
            flow['type'], flow['uuid']


class RpcJobProcessThread(gevent.greenlet.Greenlet):
    # In case server.run throws an exception, prevent
    # really aggressive spinning
    EXCEPTION_BACKOFF = 5

    def __init__(self, manager):
        super(RpcJobProcessThread, self).__init__()
        self._manager = manager
        self._complete = gevent.event.Event()

        etcd_kwargs = {
            'port': int(manager._config.get("commons", "etcd_port")),
            'host': manager._config.get("commons", "etcd_connection")
        }
        etcd_client = etcd_server(etcd_kwargs=etcd_kwargs)
        self._server = EtcdRPC(self, etcd_client)

    def stop(self):
        self._complete.set()
        if self._server:
            self._server.stop()

    def _run(self):
        while not self._complete.is_set():
            try:
                self._server.run()
            except Exception:
                LOG.error(traceback.format_exc())
                self._complete.wait(self.EXCEPTION_BACKOFF)
