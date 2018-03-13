from tendrl.commons import objects


class ClusterAlertCounters(objects.BaseObject):
    def __init__(
        self,
        alert_count=0,
        integration_id=None,
        *args,
        **kwargs
    ):
        super(ClusterAlertCounters, self).__init__(*args, **kwargs)
        self.alert_count = alert_count
        self.integration_id = integration_id
        self.value = '/clusters/{0}/alert_counters'

    def render(self):
        self.value = self.value.format(
            self.integration_id or NS.tendrl_context.integration_id
        )
        return super(ClusterAlertCounters, self).render()
