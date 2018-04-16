from tendrl.commons import objects
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import time_utils


class ClusterNodeContext(objects.BaseObject):

    def __init__(self, integration_id=None,
                 node_id=None, fqdn=None, ipv4_addr=None,
                 updated_at=None, tags=None, status=None,
                 sync_status=None, last_sync=None,
                 first_sync_done=None, is_managed=None,
                 *args, **kwargs):
        super(ClusterNodeContext, self).__init__(*args, **kwargs)
        _node_context = NS.node_context.load()
        self.integration_id = integration_id
        self.node_id = node_id or _node_context.node_id
        self.fqdn = fqdn or _node_context.fqdn
        self.ipv4_addr = ipv4_addr or _node_context.ipv4_addr
        self.updated_at = updated_at or str(time_utils.now())
        self.tags = tags or _node_context.tags
        self.status = status or _node_context.status
        self.sync_status = sync_status or _node_context.sync_status
        self.last_sync = last_sync or _node_context.last_sync
        self.first_sync_done = first_sync_done
        self.is_managed = is_managed
        self.value = 'clusters/{0}/nodes/{1}/NodeContext'

    def render(self):
        self.value = self.value.format(
            self.integration_id or NS.tendrl_context.integration_id,
            self.node_id
        )
        return super(ClusterNodeContext, self).render()

    def save(self, update=True, ttl=None):
        super(ClusterNodeContext, self).save(update)
        status = self.value + "/status"
        if ttl:
            etcd_utils.refresh(status, ttl)

    def on_change(self, attr, prev_value, current_value):
        return
