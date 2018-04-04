from tendrl.commons import objects


class Node(objects.BaseObject):
    def __init__(self, node_id=None, fqdn=None,
                 status=None, *args, **kwargs):
        super(Node, self).__init__(*args, **kwargs)
        self.list = 'nodes/'
        self.node_id = node_id
        self.fqdn = fqdn
        self.status = status
        self.value = 'nodes/{0}'

    def render(self):
        self.value = self.value.format(
            self.node_id or NS.node_context.node_id
        )
        return super(Node, self).render()
