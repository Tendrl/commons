from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.message import Message


class ImportCluster(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(ImportCluster, self).__init__(*args, **kwargs)

    def run(self):
        super(ImportCluster, self).run()
