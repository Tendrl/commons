import json

from tendrl.commons import objects


class ClusterNodeContext(objects.BaseObject):

    def __init__(self, machine_id=None, node_id=None, fqdn=None,
                 tags=None, status=None, *args, **kwargs):
        super(ClusterNodeContext, self).__init__(*args, **kwargs)
        _node_context = NS.node_context.load()
        self.machine_id = machine_id or _node_context.machine_id
        self.node_id = node_id or _node_context.node_id
        self.fqdn = fqdn or _node_context.fqdn
        self.tags = tags or _node_context.tags
        self.status = status or _node_context.status
        self.value = 'clusters/{0}/nodes/{1}/NodeContext'

    def render(self):
        self.value = self.value.format(NS.tendrl_context.integration_id,
                                       self.node_id)
        return super(ClusterNodeContext, self).render()
