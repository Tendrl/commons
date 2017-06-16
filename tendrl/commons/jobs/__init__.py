import json
import datetime
import traceback


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
                priority="debug",
                publisher=NS.publisher_id,
                payload={"message": "%s running" % self.__class__.__name__}
            )
        )
        while not self._complete.is_set():
            _job_sync_interval = 5
            NS.node_context = NS.node_context.load()
            if "tendrl/monitor" in NS.node_context.tags:
                _job_sync_interval = 3

            gevent.sleep(_job_sync_interval)
            jid = None
            try:
                try:
                    jobs = NS._int.client.read("/queue")
                except etcd.EtcdKeyNotFound:
                    continue
                
                for job in jobs.leaves:
                    jid = job.key.split('/')[-1]
                    job_status_key = "/queue/%s/status" % jid
                    job_lock_key = "/queue/%s/locked_by" % jid
                    NS.node_context = NS.node_context.load()
                    # Check job not already locked by some agent
                    try:
                        _locked_by = NS._int.client.read(job_lock_key).value
                        if _locked_by:
                            continue
                    except etcd.EtcdKeyNotFound:
                        pass
                    
                    # Check job not already "finished", or "processing"
                    try:
                        _status = NS._int.client.read(job_status_key).value
                        if _status in ["finished", "processing"]:
                            continue
                    except etcd.EtcdKeyNotFound:
                        pass

                    # tendrl-node-agent tagged as tendrl/monitor will ensure
                    # >10 min old "new" jobs are timed out and marked as
                    # "failed" (the parent job of these jobs will also be
                    # marked as "failed")
                    if "tendrl/monitor" in NS.node_context.tags:
                        _job_valid_until_key = "/queue/%s/valid_until" % jid
                        _valid_until = None
                        try:
                            _valid_until = NS._int.client.read(
                                _job_valid_until_key).value
                        except etcd.EtcdKeyNotFound:
                            pass

                        if _valid_until:
                            _now_epoch = (time_utils.now() -
                                          datetime.datetime(1970, 1,
                                                            1).replace(
                                              tzinfo=utc)).total_seconds()
                            if int(_now_epoch) >= int(_valid_until):
                                # Job has "new" status since 10 minutes,
                                # mark status as "failed" and Job.error =
                                # "Timed out"
                                try:
                                    NS._int.wclient.write(job_status_key,
                                                          "failed",
                                                          prevValue="new")
                                except etcd.EtcdCompareFailed:
                                    pass
                                else:
                                    job = Job(job_id=jid).load()
                                    _msg = str("Timed-out (>10min as 'new')")
                                    job.errors = _msg
                                    job.save()
                                    continue
                        else:
                            _now_plus_10 = time_utils.now() + \
                                          datetime.timedelta(minutes=10)
                            _epoch_start = datetime.datetime(1970, 1,
                                                             1).replace(
                                tzinfo=utc)

                            # noinspection PyTypeChecker
                            _now_plus_10_epoch = (_now_plus_10 -
                                                 _epoch_start).total_seconds()
                            NS._int.wclient.write(_job_valid_until_key,
                                                  int(_now_plus_10_epoch))

                    job = Job(job_id=jid).load()
                    if job.payload["type"] == NS.type and \
                            job.status == "new":
                        # Job routing
                        # Flows created by tendrl-api use 'tags' from flow
                        # definition to target jobs
                        _tag_match = False
                        if job.payload.get("tags", []):
                            for flow_tag in job.payload['tags']:
                                if flow_tag in NS.node_context.tags:
                                    _tag_match = True

                        # Flows created by tendrl backend use 'node_ids' to
                        # target jobs
                        _node_id_match = False
                        if job.payload.get("node_ids", []):
                            if NS.node_context.node_id in \
                                    job.payload['node_ids']:
                                _node_id_match = True
                        
                        if not _tag_match and not _node_id_match:
                            _job_node_ids = ", ".join(job.payload.get(
                                "node_ids", []))
                            _job_tags = ", ".join(job.payload.get("tags", []))
                            _msg = "Node (%s)(type: %s)(tags: %s) will not " \
                                   "process job-%s (node_ids: %s)(tags: %s)" %\
                                   (NS.node_context.node_id, NS.type,
                                    json.dumps(NS.node_context.tags), jid,
                                    _job_node_ids, _job_tags)
                            Event(
                                Message(
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": _msg}
                                )
                            )
                            continue

                        job_status_key = "/queue/%s/status" % job.job_id
                        job_lock_key = "/queue/%s/locked_by" % job.job_id
                        try:
                            lock_info = dict(node_id=NS.node_context.node_id,
                                             fqdn=NS.node_context.fqdn,
                                             tags=NS.node_context.tags,
                                             type=NS.type)
                            NS._int.wclient.write(job_lock_key,
                                                  json.dumps(lock_info))
                            NS._int.wclient.write(job_status_key, "processing",
                                                  prevValue="new")
                        except etcd.EtcdCompareFailed:
                            # job is already being processed by some tendrl
                            # agent
                            continue

                        current_ns, flow_name, obj_name = \
                            self._extract_fqdn(job.payload['run'])

                        if obj_name:
                            runnable_flow = current_ns.ns.get_obj_flow(
                                obj_name, flow_name)
                        else:
                            runnable_flow = current_ns.ns.get_flow(flow_name)
                        try:
                            the_flow = runnable_flow(parameters=job.payload[
                                'parameters'], job_id=job.job_id)
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
                                    flow_id=the_flow.parameters['flow_id'],
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": "Running Flow %s" %
                                                        job.payload['run']
                                             }
                                )
                            )
                            the_flow.run()
                            try:
                                NS._int.wclient.write(job_status_key,
                                                      "finished",
                                                      prevValue="processing")
                            except etcd.EtcdCompareFailed:
                                # This should not happen!
                                _msg = "Cannot mark job as 'finished', " \
                                       "current job status invalid"
                                raise FlowExecutionFailedError(_msg)

                            Event(
                                Message(
                                    job_id=job.job_id,
                                    flow_id=the_flow.parameters['flow_id'],
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": "Job (%s):  Finished "
                                                        "Flow %s" % (
                                                            job.job_id,
                                                            job.payload['run'])
                                             }
                                )
                            )
                        except (FlowExecutionFailedError,
                                AtomExecutionFailedError,
                                Exception) as e:
                            _trace = str(traceback.format_exc(e))
                            _msg = "Failure in Job %s Flow %s with error:" % \
                                (job.job_id, the_flow.parameters['flow_id'])
                            Event(
                                ExceptionMessage(
                                    priority="error",
                                    publisher=NS.publisher_id,
                                    payload={"message": _msg + _trace,
                                             "exception": e
                                             }
                                )
                            )
                            Event(
                                Message(
                                    job_id=job.job_id,
                                    flow_id=the_flow.parameters['flow_id'],
                                    priority="error",
                                    publisher=NS.publisher_id,
                                    payload={"message": "Job failed %s" % _trace}
                                )
                            ) 
                            try:
                                NS._int.wclient.write(job_status_key,
                                                      "failed",
                                                      prevValue="processing")
                            except etcd.EtcdCompareFailed:
                                # This should not happen!
                                _msg = "Cannot mark job as 'failed', current" \
                                       "job status invalid"
                                raise FlowExecutionFailedError(_msg)
                            else:
                                job = job.load()
                                job.errors = _trace
                                job.save()
                                                          
            except Exception as ex:
                _trace = str(traceback.format_exc(ex))
                _msg = "Job (%s) processing failure, error:" % jid
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": _msg + _trace,
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


