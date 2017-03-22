import logging
import os
import socket
import uuid

from tendrl.commons.etcdobj import EtcdObj
from tendrl.commons.utils import cmd_utils

from tendrl.commons import objects


LOG = logging.getLogger(__name__)


class ClusterNodeContext(objects.BaseObject):

    def __init__(self, machine_id=None, node_id=None, fqdn=None,
                 tags=None, status=None, *args, **kwargs):
        super(ClusterNodeContext, self).__init__(*args, **kwargs)
        self.value = 'clusters/%s/nodes/%s/NodeContext'
        self.machine_id = machine_id or NS.node_context.machine_id
        self.node_id = node_id or NS.node_context.node_id
        self.fqdn = fqdn or NS.node_context.fqdn
        self.tags = tags or NS.config.data['tags']
        self.status = status or "UP"
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
