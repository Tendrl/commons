from tendrl.commons.objects.alert import Alert

from tendrl.commons import objects


class NodeAlert(Alert, objects.BaseObject):
    def __init__(self, *args, **kwargs):
        super(NodeAlert, self).__init__(
            *args,
            **kwargs
        )
        self.value = 'alerting/nodes/{0}/{1}'

    def render(self):
        self.value = self.value.format(self.node_id, self.alert_id)
        return super(NodeAlert, self).render()
