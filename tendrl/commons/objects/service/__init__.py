
from tendrl.commons.utils import service_status

from tendrl.commons import objects


class Service(objects.BaseObject):
    def __init__(self, service=None, running=None, exists=None,
                 *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        service_detail = self.get_service_info(service)
        self.list = 'nodes/{0}/Services/'
        self.running = running or service_detail['running']
        self.service = service
        self.exists = exists or service_detail['exists']
        self.value = 'nodes/{0}/Services/{1}'

    def get_service_info(self, service_name):
        service = service_status.ServiceStatus(service_name)
        return {"exists": service.exists(), "running": service.status()}

    def render(self):
        self.value = self.value.format(
            NS.node_context.node_id,
            self.service.strip("@*")
        )
        return super(Service, self).render()
