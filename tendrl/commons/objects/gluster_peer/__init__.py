from tendrl.commons import objects


class GlusterPeer(objects.BaseObject):
    def __init__(
        self,
        state=None,
        connected=None,
        hostname=None,
        peer_uuid=None,
        deleted=False,
        deleted_at=None,
        node_id=None,
        integration_id=None,
        *args,
        **kwargs
    ):
        super(GlusterPeer, self).__init__(*args, **kwargs)

        self.state = state
        self.connected = connected
        self.hostname = hostname
        self.peer_uuid = peer_uuid
        self.deleted = deleted
        self.deleted_at = deleted_at
        self._node_id = node_id
        self._integration_id = integration_id
        self.value = 'clusters/{0}/nodes/{1}/Peers/{2}'

    def render(self):
        self.value = self.value.format(
            self._integration_id or NS.tendrl_context.integration_id,
            self._node_id or NS.node_context.node_id, self.peer_uuid
        )
        return super(GlusterPeer, self).render()
