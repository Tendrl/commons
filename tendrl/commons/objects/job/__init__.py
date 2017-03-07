from tendrl.commons import etcdobj
from tendrl.commons import objects


class Job(objects.BaseObject):
    def __init__(self, job_id=None, integration_id=None,
                 run=None, status=None, parameters=None,
                 type=None, node_ids=None, request_id=None,
                 parent=None, errors=None):
        super(Job, self).__init__(
            attrs=None,
            enabled=None,
            obj_list=None,
            obj_value=None,
            atoms=None,
            flows=None
        )
        self.value = 'queue/%s'
        self.job_id = job_id
        self.integration_id = integration_id
        self.run = run
        self.status = status
        self.parameters = parameters
        self.type = type
        self.node_ids = node_ids
        self.request_id = request_id
        self.parent = parent
        self.errors = errors
        self._etcd_cls = _JobEtcd


class _JobEtcd(etcdobj.EtcdObj):
    """Job etcd object, lazily updated
    """
    __name__ = 'queue/%s'
    _tendrl_cls = Job

    def render(self):
        self.__name__ = self.__name__ % self.job_id
        return super(_JobEtcd, self).render()
