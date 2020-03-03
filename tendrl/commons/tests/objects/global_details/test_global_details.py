import builtins
import maps
from mock import patch
import uuid

from tendrl.commons.objects.cluster_tendrl_context import ClusterTendrlContext
from tendrl.commons.objects.global_details import GlobalDetails
from tendrl.commons.utils import etcd_utils


# tests __init__ and render
def test_render():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = "test_integration_id"

    # TODO(nathan-weinberg) Without the following two lines, this tests somehow
    # causes an error in "test_gluster_peer_init.py"
    # Find out why
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = str(uuid.uuid4())

    gd_obj = GlobalDetails()
    gd_obj.render()


# test save
# simulates 'delete' method from 'etcd_utils'
@patch.object(etcd_utils, 'delete')
# simulates 'read' method from 'etcd_utils'
@patch.object(etcd_utils, 'read')
# simulates 'write' method from 'etcd_utils'
@patch.object(etcd_utils, 'write')
# simulates 'refresh' method from 'etcd_utils'
@patch.object(etcd_utils, 'refresh')
def test_save(patch_etcd_utils_delete,
              patch_etcd_utils_read,
              patch_etcd_utils_write,
              patch_etcd_utils_refresh):
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = "test_integration_id"
    NS._int.watchers = maps.NamedDict()

    # TODO(nathan-weinberg) Without the following two lines, this tests somehow
    # causes an error in "test_gluster_peer_init.py"
    # Find out why
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = str(uuid.uuid4())

    gd_obj = GlobalDetails()

    # Test with ttl
    gd_obj.save(ttl="test")
    # Test without ttl
    gd_obj.save()


# tests on_change and on_change_status
# simulates 'delete' method from 'etcd_utils'
@patch.object(etcd_utils, 'delete')
# simulates 'read' method from 'etcd_utils'
@patch.object(etcd_utils, 'read')
# simulates 'write' method from 'etcd_utils'
@patch.object(etcd_utils, 'write')
# simulates 'refresh' method from 'etcd_utils
@patch.object(etcd_utils, 'refresh')
def test_on_change(patch_etcd_utils_refresh,
                   patch_etcd_utils_write,
                   patch_etcd_utils_read,
                   patch_etcd_utils_delete):
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = "test_integration_id"
    NS.tendrl_context.cluster_name = "test_cluster_name"
    NS._int.watchers = maps.NamedDict()
    NS.publisher_id = "node_context"

    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.ClusterTendrlContext = ClusterTendrlContext

    patch_etcd_utils_read.return_value = maps.NamedDict(
        value='{"integration_id" : "test_integration_id"}'
    )

    # TODO(nathan-weinberg) Without the following two lines, this tests somehow
    # causes an error in "test_gluster_peer_init.py"
    # Find out why
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = str(uuid.uuid4())

    gd_obj = GlobalDetails()

    gd_obj.on_change("status", None, None)
