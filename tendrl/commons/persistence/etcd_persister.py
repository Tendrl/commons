from tendrl.commons.etcdobj.etcdobj import Server as etcd_server
from tendrl.commons.persistence.persister import Persister


class EtcdPersister(Persister):
    def __init(self, config):
        super(EtcdPersister, self).__init__(config)

    def get_store(self):
        etcd_kwargs = {
            'port': int(self._config.get("commons", "etcd_port")),
            'host': self._config.get("commons", "etcd_connection")
        }
        return etcd_server(etcd_kwargs=etcd_kwargs)
