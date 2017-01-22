from tendrl.commons.persistence.persister import Persister


class EtcdPersister(Persister):
    def __init__(self):
        super(EtcdPersister, self).__init__()
