from tendrl.commons import objects
from tendrl.commons.utils import service_status


class Service(objects.BaseObject):
    def __init__(self, service=None, running=None, exists=None,
                 node_id=None, error=None, *args, **kwargs):
        super(Service, self).__init__(*args, **kwargs)
        service_detail = self.get_service_info(service)
        self.list = 'nodes/{0}/Services/'
        self.running = running or service_detail['running']
        self.service = service
        self.exists = exists or service_detail['exists']
        self.node_id = node_id or NS.node_context.node_id
        self.error = error or service_detail['error']
        self.value = 'nodes/{0}/Services/{1}'

    def get_service_info(self, service_name):
        error = []
        service = service_status.ServiceStatus(service_name)
        service_exists, err = service.exists()
        if err:
            error.append(err)
        service_running, err = service.status()
        if err:
            error.append(err)
        return {"exists": service_exists,
                "running": service_running,
                "error": error
                }

    def render(self):
        self.value = self.value.format(
            self.node_id,
            self.service.strip("@*")
        )
        return super(Service, self).render()
