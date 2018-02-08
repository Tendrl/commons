from tendrl.commons import objects


class ClusterNodeAlertCounters(objects.BaseObject):
    def __init__(
        self,
        warn_count=0,
        node_id=None,
        integration_id=None,
        *args,
        **kwargs
    ):
        super(ClusterNodeAlertCounters, self).__init__(*args, **kwargs)
        self.warning_count = warn_count
        self.node_id = node_id or NS.node_context.node_id
        self.integration_id = \
            integration_id or NS.tendrl_context.integration_id
        self.value = 'clusters/{0}/nodes/{1}/alert_counters'

    def render(self):
        self.value = self.value.format(self.integration_id, self.node_id)
        return super(ClusterNodeAlertCounters, self).render()
