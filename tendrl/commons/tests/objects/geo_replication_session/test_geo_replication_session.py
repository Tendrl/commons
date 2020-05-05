import builtins
import maps
import uuid

from tendrl.commons.objects.geo_replication_session \
    import GeoReplicationSession


# Testing __init__
def test_constructor():
    setattr(builtins, "NS", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = "test_integration_id"
    vol_id = "test_vol_id"
    # without pairs
    geo_replication_sesh = GeoReplicationSession(vol_id)
    # with pairs
    pairs = "test_pairs"
    geo_replication_sesh = GeoReplicationSession(vol_id, pairs=pairs)
    # for PEP8
    geo_replication_sesh.vol_id = "test_pep8"


# Tests render
def test_render():
    setattr(builtins, "NS", maps.NamedDict())
    NS.tendrl_context = maps.NamedDict()
    NS.tendrl_context.integration_id = "test_integration_id"

    # TODO(nathan-weinberg) Without the following two lines, this tests somehow
    # causes an error in "test_gluster_peer_init.py"
    # Find out why
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = str(uuid.uuid4())

    vol_id = "test_vol_id"
    geo_replication_sesh = GeoReplicationSession(vol_id)
    geo_replication_sesh.render()
