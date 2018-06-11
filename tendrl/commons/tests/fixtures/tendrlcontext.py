class TendrlContext(object):

    def __init__(self, *args):
        self.integration_id = "test_integration_id"
        self.cluster_name = "test_name"

    def load(self):
        return self
