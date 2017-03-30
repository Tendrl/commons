import json
import traceback

import etcd
import gevent.event


from tendrl.commons.event import Event
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.message import Message, ExceptionMessage
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import etcd_util


class JobConsumerThread(gevent.greenlet.Greenlet):
    EXCEPTION_BACKOFF = 5

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
            try:
                gevent.sleep(2)
                try:
                    jobs = NS.etcd_orm.client.read("/queue")
                except etcd.EtcdKeyNotFound:
                    continue

                for job in jobs.leaves:
                    try:
                        raw_job = {"job_id": job.key.split('/')[-1],
                                   "status": None,
                                   "payload": None,
                                   "errors": None
                                   }
                        result = etcd_util.read(job.key)
                        for item in result:
                            if item in raw_job:
                                raw_job[item] = result[item]
                        raw_job["payload"] = json.loads(
                            raw_job["payload"].decode('utf-8'))
                    except etcd.EtcdKeyNotFound:
                        continue

                    if raw_job['payload']["type"] == NS.type and \
                            raw_job['status'] == "new":

                        # Job routing
                        if raw_job.get("payload", {}).get("tags", []):
                            NS.node_context = NS.node_context.load()
                            tags = json.loads(NS.node_context.tags)
                            if set(tags).isdisjoint(
                                raw_job['payload']['tags']):
                                continue

                        if raw_job.get("payload", {}).get("node_ids", []):
                            if NS.node_context.node_id not in \
                                    raw_job['payload']['node_ids']:
                                continue

                        raw_job['status'] = "processing"
                        Event(
                            Message(
                                job_id=raw_job['job_id'],
                                priority="info",
                                publisher=NS.publisher_id,
                                payload={"message": "Processing Job %s" %
                                         raw_job['job_id']
                                         }
                            )
                        )
                        Job(job_id=raw_job['job_id'],
                            status=raw_job['status'],
                            payload=json.dumps(raw_job['payload']),
                            errors=raw_job['errors']).save()

                        current_ns, flow_name, obj_name = \
                            self._extract_fqdn(raw_job['payload']['run'])

                        if obj_name:
                            runnable_flow = current_ns.ns.get_obj_flow(
                                obj_name, flow_name)
                        else:
                            runnable_flow = current_ns.ns.get_flow(flow_name)
                        try:
                            
                            the_flow = runnable_flow(parameters=raw_job['payload']['parameters'],
                                                     job_id=raw_job['job_id'])
                            Event(
                                Message(
                                    job_id=raw_job['job_id'],
                                    flow_id = the_flow.parameters['flow_id'],
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": "Running Flow %s" %
                                            raw_job['payload']['run']
                                         }
                                )
                            )
                            the_flow.run()
                            raw_job['status'] = "finished"
                            Job(job_id=raw_job['job_id'],
                                status=raw_job['status'],
                                payload=json.dumps(raw_job['payload']),
                                errors=raw_job['errors']).save()
                            Event(
                                Message(
                                    job_id=raw_job['job_id'],
                                    flow_id = the_flow.parameters['flow_id'],
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": "JOB[%s]:  Finished Flow %s" %
                                            (raw_job['job_id'], raw_job['payload']['run'])
                                         }
                                )
                            )

                        except (FlowExecutionFailedError, Exception) as e:
                            Event(
                                ExceptionMessage(
                                    priority="error",
                                    publisher=NS.publisher_id,
                                    payload={"message": "error",
                                             "exception": e
                                             }
                                )
                            )
                            raw_job['status'] = "failed"
                            raw_job['errors'] = str(e)
                            Job(job_id=raw_job['job_id'],
                                status=raw_job['status'],
                                payload=json.dumps(raw_job['payload']),
                                errors=raw_job['errors']).save()
                        break
            except Exception as ex:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "error traceback",
                                 "exception": ex
                                 }
                    )
                )
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


