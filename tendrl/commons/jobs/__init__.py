import json
import logging
import traceback
import uuid

import gevent.event

from tendrl.commons.flows.exceptions import FlowExecutionFailedError

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
            if tendrl_ns.type == "node":
                raw_job['request_id'] = "nodes/%s/_jobs/%s_%s" % (
                    tendrl_ns.node_context.node_id, raw_job['run'],
                    req_id)
            else:
                raw_job['request_id'] = "clusters/%s/_jobs/%s_%s" % (
                    tendrl_ns.tendrl_context.integration_id, raw_job['run'],
                    req_id)


            # TODO(team) Convert this raw write to done via
            # persister.update_job()
            tendrl_ns.etcd_orm.client.write(job_key, json.dumps(raw_job))
            try:
                self.invoke_flow(raw_job['run'], raw_job)
            except FlowExecutionFailedError as e:
                LOG.error(e)
                raw_job['status'] = "failed"
            else:
                raw_job['status'] = "finished"

            return raw_job, True
        else:
            return raw_job, False

    def _acceptor(self):
        while not self.job_consumer_thread._complete.is_set():
            # TODO(team) replace below raw write with a "EtcdJobQueue" class
            jobs = tendrl_ns.etcd_orm.client.read("/queue")
            for job in jobs.children:
                executed = False
                if job.value is None:
                    continue
                raw_job = json.loads(job.value.decode('utf-8'))
                try:
                    # If current node's id does not fall under job's node_ids,
                    # ignore the job and dont process
                    if "node_ids" in raw_job:
                        if tendrl_ns.node_context.node_id \
                                not in raw_job['node_ids']:
                            continue
                    raw_job['parameters']['cluster_id'] = raw_job['cluster_id']
                    raw_job, executed = self._process_job(
                        raw_job,
                        job.key
                    )
                except FlowExecutionFailedError as e:
                    LOG.error(e)
                if executed:
                    # TODO(team) replace below raw write with a
                    # "EtcdJobQueue" class
                    tendrl_ns.etcd_orm.client.write(job.key, json.dumps(
                        raw_job))
                    break
            gevent.sleep(2)

    def run(self):
        self._acceptor()

    def stop(self):
        pass

    def invoke_flow(self, flow_fqn, job):
        # flow_fqn eg:tendrl.node_agent.objects.abc.flows.temp_flows
        if "tendrl" in flow_fqn and "objects" in flow_fqn:
            obj_name, flow_name = flow_fqn.split(".objects.")[-1].split(
                ".flows.")
            flow = tendrl_ns.get_obj_flow(obj_name, flow_name)
            return flow(parameters=job['parameters'],
                        request_id=job['request_id']).run()

        # flow_fqn eg: tendrl.node_agent.flows.temp_flows
        if "tendrl" in flow_fqn and "flows" in flow_fqn:
            flow_name = flow_fqn.split(".flows.")[-1]
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
