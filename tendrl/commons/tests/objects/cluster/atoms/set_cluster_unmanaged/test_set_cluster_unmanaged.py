import __builtin__
import etcd
import maps
import mock
from mock import patch

from tendrl.commons.objects.cluster.atoms.set_cluster_unmanaged \
    import SetClusterUnmanaged
from tendrl.commons.utils import etcd_utils


def test_constructor():
    SetClusterUnmanaged()


def write_success(*args):
    pass


def write_failed(*args):
    raise etcd.EtcdKeyNotFound


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    obj = SetClusterUnmanaged()
    assert obj.parameters is not None
    obj.parameters = maps.NamedDict()
    obj.parameters["TendrlContext.integration_id"] = \
        "test_uuid"
    obj.parameters["job_id"] = "test_job_id"
    obj.parameters["flow_id"] = "test_flow_id"
    setattr(__builtin__, "NS", maps.NamedDict())
    with patch.object(etcd_utils, 'write', write_success):
        ret_val = obj.run()
        assert ret_val is True
    with patch.object(etcd_utils, 'write', write_failed):
        ret_val = obj.run()
        assert ret_val is False
