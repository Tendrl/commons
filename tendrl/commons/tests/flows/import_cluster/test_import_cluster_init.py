import maps
import mock
import pytest
from mock import patch
from tendrl.commons.flows.import_cluster import ImportCluster
from tendrl.commons.flows.exceptions import FlowExecutionFailedError


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    param= maps.NamedDict()
    param['TendrlContext.integration_id'] = None
    with pytest.raises(Exception):
        import_cluster = ImportCluster(parameters = param)
        import_cluster.run()
    param['TendrlContext.integration_id'] = "Test integration_id"
    param['DetectedCluster.sds_pkg_name'] = "Test package_name"
