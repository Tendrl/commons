import etcd
import gevent.event
import json
import logging
import traceback
import uuid
import yaml

from tendrl.common.definitions.validator import DefinitionsSchemaValidator
from tendrl.common.flows.exceptions import FlowExecutionFailedError

LOG = logging.getLogger(__name__)


class EtcdRPC(object):

    def __init__(self, syncJobThread):
        self.config = syncJobThread._manager._config
        etcd_kwargs = {
            'port': int(self.config.get("common", "etcd_port")),
            'host': self.config.get("common", "etcd_connection")
        }

        self.client = etcd.Client(**etcd_kwargs)
        self.syncJobThread = syncJobThread

    def _process_job(self, raw_job, job_key, job_type):
        # Pick up the "new" job that is not locked by any other integration
        if raw_job['status'] == "new" and raw_job["type"] == job_type:
            raw_job['status'] = "processing"
            # Generate a request ID for tracking this job
            # further by tendrl-api
            req_id = str(uuid.uuid4())
            raw_job['request_id'] = "%s/flow_%s" % (
                self.syncJobThread._manager.integration_id, req_id)
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
                    raw_job, executed = self._process_job(
                        raw_job,
                        job.key,
                        job_type
                    )
                    if "etcd_client" in raw_job['parameters']:
                        del raw_job['parameters']['etcd_client']
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
        # resp, msg = JobValidator(definitions).validateApi(raw_job)
        # if resp:
        #    msg = "Successfull Validation flow %s for %s" %\
        #          (raw_job['run'], raw_job['request_id'])
        #    LOG.info(msg)

        return definitions
        # else:
        #    msg = "Failed Validation flow %s for %s" % (raw_job['run'],
        #                                               raw_job['request_id'])
        #    LOG.error(msg)
        #    return False

    def invoke_flow(self, flow_name, job, definitions):
        atoms, help, enabled, inputs, pre_run, post_run, type, uuid = \
            self.extract_flow_details(flow_name, definitions)
        the_flow = None
        flow_path = flow_name.split('.')
        flow_module = ".".join([a.encode("ascii", "ignore") for a in
                                flow_path[:-1]])
        kls_name = ".".join([a.encode("ascii", "ignore") for a in
                             flow_path[-1:]])
        if "tendrl" in flow_path and "flows" in flow_path:
            exec("from %s import %s as the_flow" % (flow_module, kls_name))
            return the_flow(flow_name, atoms, help, enabled, inputs, pre_run,
                            post_run, type, uuid, job['parameters'],
                            job, self.config, definitions).run()

    def extract_flow_details(self, flow_name, definitions):
        namespace = flow_name.split(".flows.")[0]
        flow = definitions[namespace]['flows'][flow_name.split(".")[-1]]
        return flow['atoms'], flow['help'], flow['enabled'], flow['inputs'], \
            flow['pre_run'], flow['post_run'], flow['type'], flow['uuid']


class SyncJobThread(gevent.greenlet.Greenlet):
    # In case server.run throws an exception, prevent
    # really aggressive spinning
    EXCEPTION_BACKOFF = 5

    def __init__(self, manager):
        super(SyncJobThread, self).__init__()
        self._manager = manager
        self._complete = gevent.event.Event()
        self._server = EtcdRPC(self)

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
