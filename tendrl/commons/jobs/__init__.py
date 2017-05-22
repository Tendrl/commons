import json
import traceback
import datetime


import etcd
import gevent.event
from pytz import utc


from tendrl.commons.event import Event
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.message import Message, ExceptionMessage
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import time_utils

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
            gevent.sleep(10)
            try:
                try:
                    jobs = NS._int.client.read("/queue")
                except etcd.EtcdKeyNotFound:
                    continue

                for job in jobs.leaves:
                    try:
                        jid = job.key.split('/')[-1]
                        job_status_key = "/queue/%s/status" % jid
                        NS.node_context = NS.node_context.load()

                        # tendrl-node-agent tagged as tendrl/monitor will ensure >5 mins old "new" jobs are timed out
                        # and marked as "failed" (the parent job of these jobs will also be marked as "failed")
                        if "tendrl/monitor" in NS.node_context.tags:
                            try:
                                _job_valid_until_key = "/queue/%s/valid_until" % jid
                                _valid_until = None
                                try:
                                    _valid_until = NS._int.client.read(_job_valid_until_key).value
                                except etcd.EtcdKeyNotFound:
                                    pass

                                if _valid_until:
                                    _now_epoch = (time_utils.now() - datetime.datetime(1970,1,1).replace(tzinfo=utc)).total_seconds()
                                    if int(_now_epoch) >= int(_valid_until):
                                        # Job has "new" status since 5 minutes, mark status as "failed" and Job.error = "Timed out"
                                        try:
                                            NS._int.wclient.write(job_status_key, "failed", prevValue="new")
                                        except etcd.EtcdCompareFailed:
                                            pass
                                        else:
                                            job = Job(job_id=jid).load()
                                            job.errors = str("Timed-out (>5mins as 'new')")
                                            job.save()
                                            continue
                                else:
                                    _now_plus_5 = time_utils.now() + datetime.timedelta(minutes=5)
                                    _now_plus_5_epoch = (_now_plus_5 - datetime.datetime(1970,1,1).replace(tzinfo=utc)).total_seconds()
                                    NS._int.wclient.write(_job_valid_until_key, int(_now_plus_5_epoch))

                            except etcd.EtcdException:
                                pass
                        
                        try:
                            _status = NS._int.client.read(job_status_key).value
                            if _status in ["finished", "processing"]:
                                continue
                            _seen_by_key = "/queue/%s/_seen_by_%s" % (jid, NS.node_context.node_id)
                            NS._int.client.read(_seen_by_key)
                            # Job already seen (could not match) by $this node
                            continue
                        except etcd.EtcdKeyNotFound:
                            pass
                        
                        try:
                            _locked_by_key = "/queue/%s/locked_by" % jid
                            _locked_by = NS._int.client.read(_locked_by_key).value
                            if _locked_by:
                                # Job already locked by other node
                                continue
                        except etcd.EtcdKeyNotFound:
                            pass

                        job = Job(job_id=jid).load()

                    except etcd.EtcdKeyNotFound:
                        continue

                    if job.payload["type"] == NS.type and \
                            job.status == "new":

                        # Job routing
                        
                        # Flows created by tendrl-api use 'tags' from flow definition to target jobs
                        _tag_match = False
                        if job.payload.get("tags", []):
                            for flow_tag in job.payload['tags']:
                                if flow_tag in NS.node_context.tags:
                                    _tag_match = True

                        # Flows created by tendrl backend use 'node_ids' to target jobs
                        _node_id_match = False
                        if job.payload.get("node_ids", []):
                            if NS.node_context.node_id in \
                                    job.payload['node_ids']:
                                _node_id_match = True
                        
                        if not _tag_match and not _node_id_match:
                            _job_node_ids = ", ".join(job.payload.get("node_ids",
                                                                          []))
                            _job_tags = ", ".join(job.payload.get("tags", []))
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
                            NS._int.wclient.write(_seen_by_key, True)
                            continue

                        job_status_key = "/queue/%s/status" % job.job_id
                        job_lock_key = "/queue/%s/locked_by" % job.job_id
                        try:
                            lock_info = dict(node_id=NS.node_context.node_id, fqdn=NS.node_context.fqdn,
                                             tags=NS.node_context.tags)
                            NS._int.wclient.write(job_lock_key, json.dumps(lock_info))
                            NS._int.wclient.write(job_status_key, "processing", prevValue="new")
                        except etcd.EtcdCompareFailed:
                            # job is already being processed by some tendrl agent
                            continue

                        current_ns, flow_name, obj_name = \
                            self._extract_fqdn(job.payload['run'])

                        if obj_name:
                            runnable_flow = current_ns.ns.get_obj_flow(
                                obj_name, flow_name)
                        else:
                            runnable_flow = current_ns.ns.get_flow(flow_name)
                        try:
                            job = job.load()
                            job.output = {"_None": "_None"}
                            job.save()
                            
                            the_flow = runnable_flow(parameters=job.payload['parameters'],
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
                                                        job.payload['run']
                                         }
                                )
                            )
                            the_flow.run()
                            try:
                                NS._int.wclient.write(job_status_key, "finished", prevValue="processing")
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
                                            (job.job_id, job.payload['run'])
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
                                NS._int.wclient.write(job_status_key, "failed", prevValue="processing")
                            except etcd.EtcdCompareFailed:
                                # This should not happen!
                                raise FlowExecutionFailedError("Cannnot mark job as 'failed', current job status invalid")
                            else:
                                job = job.load()
                                job.errors = str(e)
                                job.save()
                                                          
            except Exception as ex:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "Job processing failure, error:" +
                                            ex.message,
                                 "exception": ex
                                 }
                    )
                )
                pass

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


