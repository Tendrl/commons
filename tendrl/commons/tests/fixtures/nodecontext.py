class NodeContext(object):

    def __init__(self, node_id=None, *args):
        self.tags = "test_tag"
        self.fqdn = "test_fqdn"
        self.node_id = node_id

    def load(self):
        return self
