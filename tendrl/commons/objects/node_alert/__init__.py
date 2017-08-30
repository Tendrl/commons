from tendrl.commons.objects.alert import Alert

from tendrl.commons import objects


class NodeAlert(Alert, objects.BaseObject):
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
        classification=None,
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
        super(NodeAlert, self).__init__(
            alert_id,
            node_id,
            time_stamp,
            resource,
            current_value,
            tags,
            alert_type,
            severity,
            classification,
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
        self.value = 'alerting/nodes/{0}/{1}'

    def render(self):
        self.value = self.value.format(self.node_id, self.alert_id)
        return super(NodeAlert, self).render()
