import json

from tendrl.commons import objects
from tendrl.commons.objects.alert import Alert


class UtilizationOnlyAlert(Alert, objects.BaseObject):
    def __init__(self, *args, **kwargs):
        super(UtilizationOnlyAlert, self).__init__(
            *args,
            **kwargs
        )
        self.value = 'alerting/notify/{0}'

    def render(self):
        try:
            self.tags = json.loads(self.tags)
        except(TypeError, ValueError):
            # Already in json or None
            pass
        self.value = self.value.format(self.alert_id)
        return super(UtilizationOnlyAlert, self).render()
