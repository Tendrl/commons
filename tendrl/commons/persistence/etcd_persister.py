from tendrl.commons.persistence.persister import Persister


class EtcdPersister(Persister):
    def __init__(self, etcd_client):
        super(EtcdPersister, self).__init__()
        # Child classes responsible to provide valid etcd client
        self.etcd_client = etcd_client
