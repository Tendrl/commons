from tendrl.commons.persistence.persister import Persister


class FilePersister(Persister):
    def __init(self, config):
        super(FilePersister, self).__init__(config)
