import maps
from mock import patch

from tendrl.commons.objects.cluster.atoms.is_cluster_import_ready \
    import IsClusterImportReady
from tendrl.commons.utils import etcd_utils


def test_run():
    icir_obj = IsClusterImportReady()
    icir_obj.parameters = maps.NamedDict()
    icir_obj.parameters['TendrlContext.integration_id'] = 'test_integration_id'

    # with node ids
    with patch.object(etcd_utils, 'read'):
        icir_obj.run()

    # TODO(nathan-weinberg): Add additional coverage
