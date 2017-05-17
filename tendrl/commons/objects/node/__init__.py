

from tendrl.commons import objects


class Node(objects.BaseObject):
    def __init__(self, fqdn=None,
                 status=None, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.list = 'nodes/'
        self.fqdn = fqdn
        self.status = status
        self.value = 'nodes/{0}'

    def render(self):
        self.value = self.value.format(NS.node_context.node_id)
        return super(Node, self).render()
