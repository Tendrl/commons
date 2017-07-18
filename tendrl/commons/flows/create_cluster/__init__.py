from tendrl.commons import flows
from tendrl.commons.event import Event
from tendrl.commons.message import Message


class CreateCluster(flows.BaseFlow):
    def __init__(self, *args, **kwargs):
        super(CreateCluster, self).__init__(*args, **kwargs)

    def run(self):
        super(CreateCluster, self).run()
