import json

from tendrl.commons import objects
from tendrl.commons.objects.alert import Alert


class ClusterAlert(Alert, objects.BaseObject):
    def __init__(self, *args, **kwargs):
        super(ClusterAlert, self).__init__(
            *args,
            **kwargs
        )
        self.value = 'alerting/clusters/{0}/{1}'

    def render(self):
        try:
            self.tags = json.loads(self.tags)
        except TypeError:
            # Already in json format
            pass
        self.value = self.value.format(
            self.tags['integration_id'],
            self.alert_id
        )
        return super(ClusterAlert, self).render()
