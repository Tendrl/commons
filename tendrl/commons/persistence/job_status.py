from tendrl.commons.etcdobj.etcdobj import EtcdObj
from tendrl.commons.etcdobj import fields


class JobStatus(EtcdObj):
    """Tendrl Job status and info

    """
    __name__ = '%s'

    req_id = fields.StrField("req_id")
    log_all = fields.StrField("all")
    log_info = fields.StrField("info")
    log_error = fields.StrField("error")
    log_warn = fields.StrField("warn")
    log_debug = fields.StrField("debug")


    def render(self):
        self.__name__ = self.__name__ % self.req_id
        return super(JobStatus, self).render()