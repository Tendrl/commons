from tendrl.commons import etcdobj
from tendrl.commons import objects


class Job(objects.BaseObject):
    def __init__(self, job_id=None, payload=None,
                 status=None, errors=None, *args,
                 **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.value = 'queue/%s'
        self.job_id = job_id
        self.status = status
        self.payload = payload
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
