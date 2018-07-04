import __builtin__
import maps
from mock import patch

from tendrl.commons.objects.gluster_brick import GlusterBrick
from tendrl.commons.objects.gluster_volume import GlusterVolume
from tendrl.commons.utils import etcd_utils


# Tests __init__ and render
def test_render():
    gluster_brick_obj = GlusterBrick(
        integration_id="test_integration_id",
        fqdn="test_fqdn"
    )
    gluster_brick_obj.render()


# Tests save
# simulates 'read' method from 'etcd_utils'
@patch.object(etcd_utils, 'read')
# simulates 'delete' method from 'etcd_utils'
@patch.object(etcd_utils, 'delete')
# simulates 'write' method from 'etcd_utils'
@patch.object(etcd_utils, 'write')
# simulates 'refresh' method from 'etcd_utils'
@patch.object(etcd_utils, 'refresh')
def test_save(patch_etcd_utils_refresh,
              patch_etcd_utils_write,
              patch_etcd_utils_delete,
              patch_etcd_utils_read):
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.GlusterVolume = GlusterVolume
    NS._int.watchers = maps.NamedDict()

    patch_etcd_utils_read.return_value = maps.NamedDict(
        value='{"vol_id" : "vol_id"}'
    )

    # IMPORTANT: Without the following two lines, this tests somehow
    # causes an error in "test_gluster_peer_init.py"
    # Find out why
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = 1

    gluster_brick_obj = GlusterBrick(
        integration_id="test_integration_id",
        fqdn="test_fqdn"
    )

    # with ttl
    gluster_brick_obj.save(ttl="test")
    # without ttl
    gluster_brick_obj.save()
