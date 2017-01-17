from tendrl.commons.persistence.persister import Persister


class EtcdPersister(Persister):
    def __init__(self, etcd_orm):
        super(EtcdPersister, self).__init__()
        # Child classes responsible to provide valid etcdobj Server (orm)
        self.etcd_orm = etcd_orm
