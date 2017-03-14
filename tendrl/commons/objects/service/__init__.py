from tendrl.commons import etcdobj
from tendrl.commons.utils import service_status

from tendrl.commons import objects


class Service(objects.BaseObject):
    def __init__(self, service=None, running=None, exists=None,
                 *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        service_detail = self.get_service_info(service)
        self.value = 'nodes/%s/Services/%s'
        self.list = 'nodes/%s/Services/'
        self.running = running or service_detail['running']
        self.service = service
        self.exists = exists or service_detail['exists']
        self._etcd_cls = _ServiceEtcd

    def get_service_info(self, service_name):
        service = service_status.ServiceStatus(service_name)
        return {"exists": service.exists(), "running": service.status()}


class _ServiceEtcd(etcdobj.EtcdObj):
    """A table of the service, lazily updated

    """
    __name__ = 'nodes/%s/Service/%s'
    _tendrl_cls = Service

    def render(self):
        self.__name__ = self.__name__ % (
            NS.node_context.node_id,
            self.service.strip("@*")
        )
        return super(_ServiceEtcd, self).render()
