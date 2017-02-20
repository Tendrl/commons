import gevent.event
import gevent.greenlet
import gevent.queue

from tendrl.commons.event import Event
from tendrl.commons.message import Message


class CentralStore(gevent.greenlet.Greenlet):
    def __init__(self):
        super(CentralStore, self).__init__()
        self._complete = gevent.event.Event()

    def _run(self):
        Event(
            Message(
                priority="info",
                publisher=tendrl_ns.publisher_id,
                payload={"message": "Central Store listening"}
            )
        )
        while not self._complete.is_set():
            gevent.sleep(0.1)

    def stop(self):
        self._complete.set()


class EtcdCentralStore(CentralStore):
    def __init__(self):
        super(EtcdCentralStore, self).__init__()

    def save_job(self, job):
        NS.etcd_orm.save(job)
    
    def save_clustertendrlcontext(self, cluster_tendrl_context):
        NS.etcd_orm.save(cluster_tendrl_context)

    def save_clusternodecontext(self, cluster_node_context):
        NS.etcd_orm.save(cluster_node_context)

    def save_nodecontext(self, node_context):
        NS.etcd_orm.save(node_context)

    def save_definition(self, definition):
        NS.etcd_orm.save(definition)

    def save_detectedcluster(self, detected_cluster):
        NS.etcd_orm.save(detected_cluster)

    def save_platform(self, platform):
        NS.etcd_orm.save(platform)

    def save_tendrlcontext(self, tendrl_context):
        NS.etcd_orm.save(tendrl_context)

    def save_service(self, service):
        NS.etcd_orm.save(service)

    def save_cpu(self, cpu):
        NS.etcd_orm.save(cpu)

    def save_disk(self, disk):
        NS.etcd_orm.save(disk)

    def save_file(self, file):
        NS.etcd_orm.save(file)

    def save_memory(self, memory):
        NS.etcd_orm.save(memory)

    def save_node(self, node):
        NS.etcd_orm.save(node)

    def save_os(self, os):
        NS.etcd_orm.save(os)

    def save_package(self, package):
        NS.etcd_orm.save(package)
