import json
import traceback

import etcd
import gevent.event


from tendrl.commons.event import Event
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.message import Message, ExceptionMessage
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects.job import Job


class JobConsumerThread(gevent.greenlet.Greenlet):

    def __init__(self):
        super(JobConsumerThread, self).__init__()
        self._complete = gevent.event.Event()

    def _run(self):
        Event(
            Message(
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "%s running" % self.__class__.__name__}
            )
        )
        while not self._complete.is_set():
            gevent.sleep(2)
            try:
                try:
                    jobs = NS.etcd_orm.client.read("/queue")
                except etcd.EtcdKeyNotFound:
                    continue

                for job in jobs.leaves:
                    try:
                        jid = job.key.split('/')[-1]
                        
                        try:
                            _seen_by_key = "/queue/%s/_seen_by_%s" % (jid, NS.node_context.node_id)
                            NS.etcd_orm.client.read(_seen_by_key)
                            # Job already seen (could not match) by $this node
                            continue
                        except etcd.EtcdKeyNotFound:
                            pass
                        
                        try:
                            _locked_by_key = "/queue/%s/locked_by" % jid
                            _locked_by = NS.etcd_orm.client.read(_locked_by_key).value
                            if _locked_by:
                                # Job already locked by other node
                                continue
                        except etcd.EtcdKeyNotFound:
                            pass

                        job = Job(job_id=jid).load()
                        raw_job = {}
                        raw_job["payload"] = json.loads(job.payload.decode('utf-8'))
                    except etcd.EtcdKeyNotFound:
                        continue

                    if raw_job['payload']["type"] == NS.type and \
                            job.status == "new":

                        # Job routing
                        
                        # Flows created by tendrl-api use 'tags' from flow definition to target jobs
                        _tag_match = False
                        NS.node_context = NS.node_context.load()
                        NS.node_context.tags = json.loads(NS.node_context.tags)
                        if raw_job.get("payload", {}).get("tags", []):
                            for flow_tag in raw_job['payload']['tags']:
                                if flow_tag in NS.node_context.tags:
                                    _tag_match = True

                        # Flows created by tendrl backend use 'node_ids' to target jobs
                        _node_id_match = False
                        if raw_job.get("payload", {}).get("node_ids", []):
                            if NS.node_context.node_id in \
                                    raw_job['payload']['node_ids']:
                                _node_id_match = True
                        
                        if not _tag_match and not _node_id_match:
                            _job_node_ids = ", ".join(raw_job.get("payload", 
                                                                  {}).get("node_ids",
                                                                          []))
                            _job_tags = ", ".join(raw_job.get("payload", {}).get("tags", []))
                            _msg = "Node (%s)(tags: %s) will not process job-%s (node_ids: %s)(tags: %s)" % (NS.node_context.node_id,
                                                                                                             json.dumps(NS.node_context.tags),
                                                                                                             jid,
                                                                                                             _job_node_ids,
                                                                                                             _job_tags)
                            Event(
                                Message(
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": _msg}
                                )
                            )
                            _seen_by_key = "/queue/%s/_seen_by_%s" % (job.job_id, NS.node_context.node_id)
                            NS.etcd_orm.client.write(_seen_by_key, True)
                            continue

                        job_status_key = "/queue/%s/status" % job.job_id
                        job_lock_key = "/queue/%s/locked_by" % job.job_id
                        try:
                            lock_info = dict(node_id=NS.node_context.node_id, fqdn=NS.node_context.fqdn,
                                             tags=NS.node_context.tags)
                            NS.etcd_orm.client.write(job_lock_key, json.dumps(lock_info))
                            NS.etcd_orm.client.write(job_status_key, "processing", prevValue="new")
                        except etcd.EtcdCompareFailed:
                            # job is already being processed by some tendrl agent
                            continue

                        current_ns, flow_name, obj_name = \
                            self._extract_fqdn(raw_job['payload']['run'])

                        if obj_name:
                            runnable_flow = current_ns.ns.get_obj_flow(
                                obj_name, flow_name)
                        else:
                            runnable_flow = current_ns.ns.get_flow(flow_name)
                        try:
                            job = job.load()
                            job.output = {"_None": "_None"}
                            job.save()
                            
                            the_flow = runnable_flow(parameters=raw_job['payload']['parameters'],
                                                     job_id=job.job_id)
                            Event(
                                Message(
                                    job_id=job.job_id,
                                    flow_id=the_flow.parameters['flow_id'],
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": "Processing Job %s" %
                                             job.job_id
                                             }
                                )
                            )

                            Event(
                                Message(
                                    job_id=job.job_id,
                                    flow_id = the_flow.parameters['flow_id'],
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": "Running Flow %s" %
                                            raw_job['payload']['run']
                                         }
                                )
                            )
                            the_flow.run()
                            try:
                                NS.etcd_orm.client.write(job_status_key, "finished", prevValue="processing")
                            except etcd.EtcdCompareFailed:
                                # This should not happen!
                                raise FlowExecutionFailedError("Cannnot mark job as 'finished', current job status invalid")

                            Event(
                                Message(
                                    job_id=job.job_id,
                                    flow_id = the_flow.parameters['flow_id'],
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": "JOB[%s]:  Finished Flow %s" %
                                            (job.job_id, raw_job['payload']['run'])
                                         }
                                )
                            )
                        except (FlowExecutionFailedError, AtomExecutionFailedError,
                                Exception) as e:
                            _msg = "Failure in Job %s Flow %s with error: " % (job.job_id,
                                                                         the_flow.parameters['flow_id'])
                            Event(
                                ExceptionMessage(
                                    priority="error",
                                    publisher=NS.publisher_id,
                                    payload={"message": _msg + e.message,
                                             "exception": e
                                             }
                                )
                            )
                            Event(
                                Message(
                                    job_id=job.job_id,
                                    flow_id = the_flow.parameters['flow_id'],
                                    priority="error",
                                    publisher=NS.publisher_id,
                                    payload={"message": "Job failed %s: %s" % (e, e.message)}
                                )
                            ) 
                            try:
                                NS.etcd_orm.client.write(job_status_key, "failed", prevValue="processing")
                            except etcd.EtcdCompareFailed:
                                # This should not happen!
                                raise FlowExecutionFailedError("Cannnot mark job as 'failed', current job status invalid")
                            job = job.load()
                            job.errors = str(e)
                            job.save()
            except Exception as ex:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "Job /queue failure, error:" + ex.message,
                                 "exception": ex
                                 }
                    )
                )

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


