import json
import logging
import traceback
import uuid

import etcd
import gevent.event

from tendrl.commons.flows.exceptions import FlowExecutionFailedError


LOG = logging.getLogger(__name__)


class JobConsumerThread(gevent.greenlet.Greenlet):
    EXCEPTION_BACKOFF = 5

    def __init__(self):
        self._complete = gevent.event.Event()

    def _run(self):
        while not self._complete.is_set():
            try:
                gevent.sleep(2)

                # TODO(team) replace below raw write with a "EtcdJobQueue"
                # class
                # Look for job in namespace queue
                try:
                    jobs = tendrl_ns.etcd_orm.client.read(
                        "/queue")
                except etcd.EtcdKeyNotFound:
                    continue

                for job in jobs.children:
                    if job.value is None:
                        continue

                    raw_job = json.loads(job.value.decode('utf-8'))
                    if raw_job["type"] == tendrl_ns.type and \
                            raw_job['status'] == "new":

                        # TODO(ndarshan) replace this check with Tag based
                        # routing
                        if "node_ids" in raw_job:
                            if tendrl_ns.node_context.node_id not in \
                                    raw_job['node_ids']:
                                continue
                        raw_job['status'] = "processing"
                        # Generate a request ID for tracking this job
                        # further by tendrl-api
                        req_id = str(uuid.uuid4())
                        if tendrl_ns.type == "node" or \
                                tendrl_ns.type == "monitoring":
                            raw_job['request_id'] = "nodes/%s/_jobs/%s_%s" % (
                                tendrl_ns.node_context.node_id, raw_job['run'],
                                req_id)
                        else:
                            raw_job[
                                'request_id'] = "clusters/%s/_jobs/%s_%s" % (
                                tendrl_ns.tendrl_context.integration_id,
                                raw_job['run'],
                                req_id)

                        # TODO(team) Convert this raw write to done via
                        # persister.update_job()
                        tendrl_ns.etcd_orm.client.write(job.key,
                                                        json.dumps(raw_job))

                        raw_job['parameters']['integration_id'] = raw_job[
                            'integration_id']
                        raw_job['parameters']['node_ids'] = raw_job[
                            'node_ids']

                        current_ns, flow_name, obj_name = \
                            self._extract_fqdn(raw_job['run'])

                        if obj_name:
                            runnable_flow = current_ns.ns.get_obj_flow(
                                obj_name, flow_name)
                        else:
                            runnable_flow = current_ns.ns.get_flow(flow_name)
                        try:
                            runnable_flow(parameters=raw_job['parameters'],
                                          request_id=raw_job[
                                              'request_id']).run()
                            raw_job['status'] = "finished"
                            # TODO(team) replace below raw write with a
                            # "EtcdJobQueue" class
                            tendrl_ns.etcd_orm.client.write(job.key,
                                                            json.dumps(
                                                                raw_job))

                        except FlowExecutionFailedError as e:
                            LOG.error(e)
                            raw_job['status'] = "failed"

                            tendrl_ns.etcd_orm.client.write(
                                job.key, json.dumps(raw_job))

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

        if "tendrl.flows" in flow_fqdn or "tendrl.objects" in flow_fqdn:
            return tendrl_ns, flow_name, obj_name

        ns_str = ns.split(".")[-1]
        if "integrations" in ns:
            return getattr(tendrl_ns.integrations, ns_str), flow_name, obj_name
        else:
            return getattr(tendrl_ns, ns_str), flow_name, obj_name
