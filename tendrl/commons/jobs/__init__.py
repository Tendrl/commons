import json
import logging
import traceback
import uuid

import etcd
import gevent.event

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects.atoms import AtomExecutionFailedError
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import etcd_util

LOG = logging.getLogger(__name__)


class JobConsumer(object):
    def __init__(self, job_consumer_thread):
        self.job_consumer_thread = job_consumer_thread

    def _process_job(self, raw_job, job_key):
        # TODO(team) convert raw_job to a Job object
        # Pick up the "new" job that is not locked by any other integration
        # "type" can be "node" or "sds"
        if raw_job['status'] == "new" and raw_job["type"] == tendrl_ns.type:
            raw_job['status'] = "processing"
            # Generate a request ID for tracking this job
            # further by tendrl-api
            req_id = str(uuid.uuid4())
            if tendrl_ns.type == "node" or tendrl_ns.type == "monitoring":
                raw_job['request_id'] = "nodes/%s/_jobs/%s_%s" % (
                    tendrl_ns.node_context.node_id, raw_job['run'],
                    req_id)
            else:
                raw_job['request_id'] = "clusters/%s/_jobs/%s_%s" % (
                    tendrl_ns.tendrl_context.integration_id, raw_job['run'],
                    req_id)


            # TODO(team) Convert this raw write to done via
            # persister.update_job()
            Job(**raw_job).save()
            try:
                self.invoke_flow(raw_job['run'], raw_job)
            except FlowExecutionFailedError as e:
                LOG.error(e)
                raw_job['status'] = "failed"
                raw_job['errors'] = str(e)
            except AtomExecutionFailedError as e:
                LOG.error(e)
                raw_job['status'] = "failed"
                raw_job['errors'] = str(e)
            else:
                raw_job['status'] = "finished"

            return raw_job, True
        else:
            return raw_job, False

    def _acceptor(self):
        while not self.job_consumer_thread._complete.is_set():
            gevent.sleep(2)
            # TODO(team) replace below raw write with a "EtcdJobQueue" class
            try:
                jobs = tendrl_ns.etcd_orm.client.read("/queue")
            except etcd.EtcdKeyNotFound:
                continue
            for job in jobs.children:
                try:
                    raw_job = {"job_id": None,
                               "integration_id": None,
                               "run": None,
                               "status": None,
                               "parameters": None,
                               "type": None,
                               "node_ids": None,
                               "request_id": None,
                               "errors": None,
                               "parent": None}
                    job_id = job.key.split("/")[-1]
                    result = etcd_util.read(job.key)
                    result['job_id'] = job_id
                    for item in result:
                        if item in raw_job:
                            raw_job[item] = result[item]
                except etcd.EtcdKeyNotFound:
                    continue
                executed = False
                try:
                    # If current node's id does not fall under job's node_ids,
                    # ignore the job and dont process
                    if "node_ids" in raw_job:
                        if tendrl_ns.node_context.node_id \
                                not in raw_job['node_ids']:
                            continue
                    raw_job['parameters']['integration_id'] = raw_job['integration_id']
                    raw_job['parameters']['node_ids'] = raw_job['node_ids']
                    raw_job, executed = self._process_job(
                        raw_job,
                        job.key
                    )
                except FlowExecutionFailedError as e:
                    LOG.error(e)
                if executed:
                    # TODO(team) replace below raw write with a
                    # "EtcdJobQueue" class
                    Job(**raw_job).save()
                    break

    def run(self):
        self._acceptor()

    def stop(self):
        pass

    def invoke_flow(self, flow_fqn, job):
        # flow_fqn eg:tendrl.node_agent.objects.abc.flows.temp_flows
        if "tendrl" in flow_fqn and "objects" in flow_fqn:
            obj_name = flow_fqn.split(".objects.")[-1].split(".")[0]
            flow_name = flow_fqn.split(".flows.")[-1].split(".")[-1]
            flow = tendrl_ns.get_obj_flow(obj_name, flow_name)
            return flow(parameters=job['parameters'],
                        request_id=job['request_id']).run()

        # flow_fqn eg: tendrl.node_agent.flows.temp_flows
        if "tendrl" in flow_fqn and "flows" in flow_fqn:
            flow_name = flow_fqn.split(".flows.")[-1].split(".")[-1]
            flow = tendrl_ns.get_flow(flow_name)
            return flow(parameters=job['parameters'],
                        request_id=job['request_id']).run()

class JobConsumerThread(gevent.greenlet.Greenlet):
    # In case server.run throws an exception, prevent
    # really aggressive spinning
    EXCEPTION_BACKOFF = 5

    def __init__(self):
        super(JobConsumerThread, self).__init__()
        self._complete = gevent.event.Event()

        self._server = JobConsumer(self)

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
