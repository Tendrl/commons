import logging

from tendrl.commons.etcdobj import EtcdObj
from tendrl.commons import objects


LOG = logging.getLogger(__name__)


class TendrlContext(objects.BaseObject):
    def __init__(
        self,
        integration_id=None,
        cluster_id=None,
        cluster_name=None,
        sds_name=None,
        sds_version=None,
        *args, **kwargs):
        super(TendrlContext, self).__init__(*args, **kwargs)

        self.value = 'nodes/%s/TendrlContext'

        # integration_id is the Tendrl generated cluster UUID
        self.integration_id = integration_id
        self.cluster_id=cluster_id
        self.cluster_name=cluster_name
        self.sds_name=sds_name
        self.sds_version=sds_version
        self._etcd_cls = _TendrlContextEtcd


class _TendrlContextEtcd(EtcdObj):
    """A table of the tendrl context, lazily updated

    """
    __name__ = 'nodes/%s/TendrlContext'
    _tendrl_cls = TendrlContext

    def render(self):
        self.__name__ = self.__name__ % NS.node_context.node_id
        return super(_TendrlContextEtcd, self).render()
