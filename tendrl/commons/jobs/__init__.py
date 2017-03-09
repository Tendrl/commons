import json
import logging
import traceback
import uuid

import etcd
import gevent.event

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import etcd_util


LOG = logging.getLogger(__name__)


class JobConsumerThread(gevent.greenlet.Greenlet):
    EXCEPTION_BACKOFF = 5

    def __init__(self):
        super(JobConsumerThread, self).__init__()
        self._complete = gevent.event.Event()

    def _run(self):
        LOG.info("%s running" % self.__class__.__name__)
        while not self._complete.is_set():
            try:
                gevent.sleep(2)
                try:
                    jobs = NS.etcd_orm.client.read("/queue")
                except etcd.EtcdKeyNotFound:
                    continue

                for job in jobs.leaves:
                    try:
                        raw_job = {"job_id": None,
                                   "status": None,
                                   "payload": None,
                                   "errors": None
                                   }
                        result = etcd_util.read(job.key)
                        for item in result:
                            if item in raw_job:
                                raw_job[item] = result[item]
                        raw_job["payload"] = json.loads(raw_job["payload"].decode('utf-8'))
                    except etcd.EtcdKeyNotFound:
                        continue

                    if raw_job['payload']["type"] == NS.type and \
                            raw_job['status'] == "new":

                        # Job routing
                        if "tags" in raw_job['payload']:
                            if set(NS.node_context.tags).isdisjoint(raw_job[
                                                                        'payload']['tags']):
                                continue

                        if "node_ids" in raw_job['payload']:
                            if NS.node_context.node_id not in \
                                    raw_job['payload']['node_ids']:
                                continue
                        raw_job['status'] = "processing"
                        Job(job_id=raw_job['job_id'],
                            status=raw_job['status'],
                            payload=json.dumps(raw_job['payload']),
                            errors=raw_job['errors']).save()

                        raw_job['payload']['parameters']['integration_id'] = \
                            raw_job[
                            'payload']['integration_id']
                        raw_job['payload']['parameters']['node_ids'] = raw_job[
                            'payload']['node_ids']

                        current_ns, flow_name, obj_name = \
                            self._extract_fqdn(raw_job['payload']['run'])

                        if obj_name:
                            runnable_flow = current_ns.ns.get_obj_flow(
                                obj_name, flow_name)
                        else:
                            runnable_flow = current_ns.ns.get_flow(flow_name)
                        try:
                            runnable_flow(parameters=raw_job['payload']['parameters'],
                                          job_id=raw_job['job_id']).run()
                            raw_job['status'] = "finished"
                            # TODO(team) replace below raw write with a
                            # "EtcdJobQueue" class
                            Job(job_id=raw_job['job_id'],
                                status=raw_job['status'],
                                payload=json.dumps(raw_job['payload']),
                                errors=raw_job['errors']).save()
                        except FlowExecutionFailedError as e:
                            LOG.error(e)
                            raw_job['status'] = "failed"
                            raw_job['errors'] = str(e)
                            Job(job_id=raw_job['job_id'],
                                status=raw_job['status'],
                                payload=json.dumps(raw_job['payload']),
                                errors=raw_job['errors']).save()
                        break
            except Exception:
                LOG.error(traceback.format_exc())
                self._complete.wait(self.EXCEPTION_BACKOFF)

    def stop(self):
        self._complete.set()

    def _extract_fqdn(self, flow_fqdn):
        ns, flow_name = flow_fqdn.split(".flows.")
        obj_name = None

        # check if the flow is bound to any object
        try:
            ns, obj_name = ns.split(".objects.")
        except ValueError:
            pass

        ns_str = ns.split(".")[-1]
        if "integrations" in ns:
            return getattr(NS.integrations, ns_str), flow_name, obj_name
        else:
            return getattr(NS, ns_str), flow_name, obj_name
