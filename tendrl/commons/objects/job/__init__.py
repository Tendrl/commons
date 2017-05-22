import json


from tendrl.commons import objects


class Job(objects.BaseObject):
    def __init__(self, job_id=None, payload=None,
                 status=None, errors=None, children=None,
                 locked_by=None, output=None, *args, **kwargs):
        super(Job, self).__init__(*args, **kwargs)
        self.job_id = job_id
        self.status = status
        self.payload = payload
        self.errors = errors
        self.children = children
        self.locked_by = locked_by
        self.output = output or {"_None":"_None"}
        self.value = 'queue/{0}'

    def save(self):
        super(Job, self).save()
        if "parent" in self.payload:
            # Load parent job
            _parent = Job(job_id=self.payload['parent']).load()
            _children = []
            
            if _parent.children:
                # Load existing child job ids
                _children = _parent.children
                
            _children += [self.job_id]
            _parent.children = list(set(_children))
            _parent.save()

        if self.status == "failed":
            if "parent" in self.payload:
                _parent = Job(job_id=self.payload['parent']).load()
                _msg = "\n Child job %s failed" % self.job_id
                if _parent.errors:
                    _parent.errors += _msg
                else:
                    _parent.errors = _msg
                _parent.status = "failed"
                _parent.save()
                

    def render(self):
        self.value = self.value.format(self.job_id)
        return super(Job, self).render()
