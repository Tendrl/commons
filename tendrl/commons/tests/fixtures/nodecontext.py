class NodeContext(object):

    def __init__(self, *args):
        self.tags = "test_tag"
        self.fqdn = "test_fqdn"

    def load(self):
        return self
