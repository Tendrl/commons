import json
import traceback

import etcd
import gevent.event


from tendrl.commons.event import Event
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.message import Message, ExceptionMessage
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
                        job = Job(job_id=jid).load()
                        raw_job = {}
                        raw_job["payload"] = json.loads(job.payload.decode('utf-8'))
                    except etcd.EtcdKeyNotFound:
                        continue

                    if raw_job['payload']["type"] == NS.type and \
                            job.status == "new":

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

                        current_ns, flow_name, obj_name = \
                            self._extract_fqdn(raw_job['payload']['run'])

                        if obj_name:
                            runnable_flow = current_ns.ns.get_obj_flow(
                                obj_name, flow_name)
                        else:
                            runnable_flow = current_ns.ns.get_flow(flow_name)
                        try:
                            
                            the_flow = runnable_flow(parameters=raw_job['payload']['parameters'],
                                                     job_id=job.job_id)
                            job.status = "processing"
                            job.save()
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
                            job.status = "finished"
                            job.save()
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
                            job.status = "failed"
                            job.errors = str(e)
                            job.save()
                        break
            except Exception as ex:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "Job queue failure",
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


