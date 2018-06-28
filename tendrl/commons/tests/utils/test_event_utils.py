import __builtin__
import maps
from tendrl.commons.utils.event_utils import emit_event

def test_emit_event():
    setattr(__builtin__, "NS", maps.NamedDict())
    NS.publisher_id = 0
    NS.node_context = maps.NamedDict(fqdn="test", node_id="0")
    NS.tendrl_context = maps.NamedDict(integration_id="",
                                       cluster_name="",
                                       sds_name="")
    emit_event("test","test","test","test","test", tags=maps.NamedDict(entity_type="brick"))
    emit_event("test","test","test","test","test", tags=maps.NamedDict(entity_type="volume"))
