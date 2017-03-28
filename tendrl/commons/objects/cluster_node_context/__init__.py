import json

from tendrl.commons import objects

from tendrl.commons.etcdobj import EtcdObj




class ClusterNodeContext(objects.BaseObject):

    def __init__(self, machine_id=None, node_id=None, fqdn=None,
                 tags=None, status=None, *args, **kwargs):
        super(ClusterNodeContext, self).__init__(*args, **kwargs)
        self.value = 'clusters/%s/nodes/%s/NodeContext'
        _node_context = NS.node_context.load()
        self.machine_id = machine_id or _node_context.machine_id
        self.node_id = node_id or _node_context.node_id
        self.fqdn = fqdn or _node_context.fqdn
        self.tags = tags or json.loads(_node_context.tags)
        self.status = status or _node_context.status
        self._etcd_cls = _ClusterNodeContextEtcd


class _ClusterNodeContextEtcd(EtcdObj):
    """A table of the node context, lazily updated

    """
    __name__ = 'clusters/%s/nodes/%s/NodeContext'
    _tendrl_cls = ClusterNodeContext

    def render(self):
        self.__name__ = self.__name__ % (NS.tendrl_context.integration_id,
                                         NS.node_context.node_id)
        return super(_ClusterNodeContextEtcd, self).render()
