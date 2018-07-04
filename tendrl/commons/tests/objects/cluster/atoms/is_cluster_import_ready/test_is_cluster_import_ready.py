import etcd
import maps
from mock import patch
import pytest

from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects.cluster.atoms.is_cluster_import_ready \
    import IsClusterImportReady
from tendrl.commons.utils import etcd_utils


count = 0


class MockClass(object):
    def __init__(self):
        self.value = None


def read(*args):
    global count
    if count == 7:
        return MockClass()
    else:
        count += 1
        raise etcd.EtcdKeyNotFound


def test_run():
    icir_obj = IsClusterImportReady()
    icir_obj.parameters = maps.NamedDict()
    icir_obj.parameters['TendrlContext.integration_id'] = 'test_integration_id'

    # with node ids
    with patch.object(etcd_utils, 'read'):
        icir_obj.run()

    # simulate timeout
    with pytest.raises(AtomExecutionFailedError):
        with patch.object(etcd_utils, 'read', read):
            icir_obj.run()
