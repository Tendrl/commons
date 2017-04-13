import json

from tendrl.commons import etcdobj
from tendrl.commons import objects


class Job(objects.BaseObject):
    def __init__(self, job_id=None, payload=None,
                 status=None, errors=None, children=None,
                 locked_by=None, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.value = 'queue/%s'
        self.job_id = job_id
        self.status = status
        self.payload = payload
        self.errors = errors
        self.children = children
        self.locked_by = locked_by
        self._etcd_cls = _JobEtcd

    def save(self):
        super(Job, self).save()
        payload = json.loads(self.payload)
        if "parent" in payload:
            # Load parent job
            _parent = Job(job_id=payload['parent']).load()
            _children = []
            
            if _parent.children:
                # Load existing child job ids
                _children = json.loads(_parent.children)
                
            _children += [self.job_id]
            _parent.children = list(set(_children))
            _parent.save()
        
             

class _JobEtcd(etcdobj.EtcdObj):
    # Job etcd object, lazily updated

    __name__ = 'queue/%s'
    _tendrl_cls = Job

    def render(self):
        self.__name__ = self.__name__ % self.job_id
        return super(_JobEtcd, self).render()
