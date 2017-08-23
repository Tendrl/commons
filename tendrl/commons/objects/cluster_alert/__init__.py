from tendrl.commons.objects.alert import Alert

from tendrl.commons import objects


class ClusterAlert(Alert, objects.BaseObject):
    def __init__(
        self,
        alert_id=None,
        node_id=None,
        time_stamp=None,
        resource=None,
        current_value=None,
        tags=None,
        alert_type=None,
        severity=None,
        significance=None,
        ackedby=None,
        acked=None,
        ack_comment=[],
        acked_at=None,
        pid=None,
        source=None,
        delivered=None,
        *args,
        **kwargs
    ):
        super(ClusterAlert, self).__init__(
            alert_id,
            node_id,
            time_stamp,
            resource,
            current_value,
            tags,
            alert_type,
            severity,
            significance,
            ackedby,
            acked,
            ack_comment,
            acked_at,
            pid,
            source,
            delivered,
            *args,
            **kwargs
        )
        self.value = 'alerting/clusters/{0}/{1}'

    def render(self):
        self.value = self.value.format(self.tags['integration_id'],
                                       self.alert_id
                                       )
        return super(ClusterAlert, self).render()

