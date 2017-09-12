import json

from tendrl.commons import objects
from tendrl.commons.objects.alert import Alert


class NodeAlert(Alert, objects.BaseObject):
    def __init__(self, *args, **kwargs):
        super(NodeAlert, self).__init__(
            *args,
            **kwargs
        )
        self.value = 'alerting/nodes/{0}/{1}'

    def render(self):
        try:
            self.tags = json.loads(self.tags)
        except(TypeError, ValueError):
            # Already in json or None
            pass
        self.value = self.value.format(self.node_id, self.alert_id)
        return super(NodeAlert, self).render()
