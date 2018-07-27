import maps
from mock import patch

from tendrl.commons.objects.cluster.atoms.is_cluster_import_ready \
    import IsClusterImportReady
from tendrl.commons.utils import etcd_utils


count = 0


class MockClass(object):
    def __init__(self):
        self.value = None


def test_run():
    icir_obj = IsClusterImportReady()
    icir_obj.parameters = maps.NamedDict()
    icir_obj.parameters['TendrlContext.integration_id'] = 'test_integration_id'
    # with node ids
    with patch.object(etcd_utils, 'read') as r:
        r.return_value = maps.NamedDict(value=["testing"])
        icir_obj.run()
