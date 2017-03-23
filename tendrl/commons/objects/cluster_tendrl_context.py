import json
import logging
import os
import socket
import uuid

from tendrl.commons.etcdobj import EtcdObj
from tendrl.commons.utils import cmd_utils

from tendrl.commons import objects


LOG = logging.getLogger(__name__)


class ClusterTendrlContext(objects.BaseObject):

    def __init__(self, machine_id=None, node_id=None, fqdn=None,
                 tags=None, status=None, *args, **kwargs):
        super(ClusterTendrlContext, self).__init__(*args, **kwargs)
        
        self.value = 'clusters/%s/TendrlContext'
        
        # integration_id is the Tendrl generated cluster UUID
        self.integration_id = integration_id
        self.cluster_id=cluster_id
        self.cluster_name=cluster_name
        self._etcd_cls = _ClusterTendrlContextEtcd


class _ClusterTendrlContextEtcd(EtcdObj):
    """A table of the cluster tendrl context, lazily updated

    """
    __name__ = 'clusters/%s/TendrlContext'
    _tendrl_cls = ClusterTendrlContext

    def render(self):
        self.__name__ = self.__name__ % NS.node_context.node_id
        return super(_ClusterTendrlContextEtcd, self).render()
