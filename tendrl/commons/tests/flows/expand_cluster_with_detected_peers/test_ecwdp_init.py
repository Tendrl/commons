import __builtin__
import etcd
import maps
import mock
from mock import patch
import pytest

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.expand_cluster_with_detected_peers \
    import ExpandClusterWithDetectedPeers
import tendrl.commons.objects.cluster as cluster
from tendrl.commons.objects.cluster import Cluster
from tendrl.commons.objects.job import Job
from tendrl.commons.utils import etcd_utils


# Method that raises an error to test an exception
def read(index_key):
    raise etcd.EtcdKeyNotFound


# Object to Help with testing
class MockObject(object):

    def __init__(self, node_id=None, status=None, value=None,
                 integration_id=1, current_job=None):
        self.locked_by = None
        self.status = None
        self.value = None
        self.remove = None
        self.current_job = None

    def load(self):
        self.status = 'importing'
        self.value = '["Test id", "Test Node Id", "Test Node Id2"]'
        self.current_job = {"job_id": "Test Job"}
        return self


# Mock Cluster Node Context Object
class MockCNC(object):
    def __init__(self, node_id=1):
        self.first_sync_done = "yes"
        self.is_managed = None

    def load(self):
        return self


# Mock Cluster Node Context that is managed
class MockCNCManaged(object):
    def __init__(self, node_id=1):
        self.first_sync_done = "yes"
        self.is_managed = "yes"

    def load(self):
        return self


# Mock Job Object
class MockJob(object):
    def __init__(self, job_id=1, status=None, payload=None):
        self.status = "finished"
        self.job_id = job_id
        self.payload = payload

    def load(self):
        return self

    def save(self):
        pass


# Mock Job Object that does not have a finished status
class MockJobUnfinished(object):
    def __init__(self, job_id=1, status=None, payload=None):
        self.status = "test"
        self.job_id = job_id
        self.payload = payload

    def load(self):
        return self

    def save(self):
        pass


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.BaseFlow._execute_atom',
            mock.Mock(return_value=True))
@mock.patch('time.sleep',
            mock.Mock(return_value=True))
@mock.patch('tendrl.commons.objects.job.Job.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.save',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.utils.acquire_node_lock',
            mock.Mock(return_value=None))
@patch.object(etcd_utils, 'read')
@patch.object(cluster.Cluster, 'load')
def test_expand_cluster_with_detected_peers(patch_etcd_utils_read,
                                            patch_cluster_load):
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "node_context"
    expand_cluster_with_detected_peers = ExpandClusterWithDetectedPeers()
    param = maps.NamedDict()
    param['TendrlContext.integration_id'] = "test_integration_id"
    param['Node[]'] = []
    param["job_id"] = ""
    param["flow_id"] = ""
    expand_cluster_with_detected_peers.parameters = param
    patch_cluster_load.return_value = MockObject().load()
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict(Job=Job)
    NS.tendrl.objects.Cluster = Cluster
    NS.tendrl.objects.ClusterNodeContext = MockCNC
    NS.tendrl.objects.Job = MockJobUnfinished
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = "Test id"
    NS.node_context.fqdn = "Test fqdn"
    NS.node_context.tags = []
    NS.type = "Test type"
    param['TendrlContext.integration_id'] = "integration_id"
    param['TendrlContext.sds_name'] = "test_sds"
    # Run call that covers through about half of the method
    expand_cluster_with_detected_peers.run()
    # Checks for error that is called when EtcdKeyNotFound
    with patch.object(etcd_utils, "read", read):
        with pytest.raises(FlowExecutionFailedError):
            expand_cluster_with_detected_peers.run()
    # Change is managed so that the if statement (Line 85-87) gets covered
    NS.tendrl.objects.ClusterNodeContext = MockCNCManaged
    expand_cluster_with_detected_peers.run()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.BaseFlow._execute_atom',
            mock.Mock(return_value=True))
@mock.patch('time.sleep',
            mock.Mock(return_value=True))
@mock.patch('tendrl.commons.objects.job.Job.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.save',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.utils.acquire_node_lock',
            mock.Mock(return_value=None))
@patch.object(etcd_utils, 'read')
@patch.object(cluster.Cluster, 'load')
# Normal Mock Job and MockCNC cover code not covered in first test
def test_expand_cluster_with_detected_peers2(patch_etcd_utils_read,
                                             patch_cluster_load):
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "node_context"
    expand_cluster_with_detected_peers = ExpandClusterWithDetectedPeers()
    param = maps.NamedDict()
    param['TendrlContext.integration_id'] = "test_integration_id"
    param['Node[]'] = []
    param["job_id"] = ""
    param["flow_id"] = ""
    expand_cluster_with_detected_peers.parameters = param
    patch_cluster_load.return_value = MockObject().load()
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict(Job=Job)
    NS.tendrl.objects.Cluster = Cluster
    NS.tendrl.objects.ClusterNodeContext = MockCNC
    NS.tendrl.objects.Job = MockJob
    NS.node_context = maps.NamedDict()
    NS.node_context.node_id = "Test id"
    NS.node_context.fqdn = "Test fqdn"
    NS.node_context.tags = []
    NS.type = "Test type"
    param['TendrlContext.integration_id'] = "integration_id"
    param['TendrlContext.sds_name'] = "test_sds"
    expand_cluster_with_detected_peers.run()


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.BaseFlow._execute_atom',
            mock.Mock(return_value=True))
@mock.patch('time.sleep',
            mock.Mock(return_value=True))
@mock.patch('tendrl.commons.objects.job.Job.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.objects.job.Job.save',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.utils.acquire_node_lock',
            mock.Mock(return_value=None))
@patch.object(etcd_utils, 'read')
@patch.object(cluster.Cluster, 'load')
# Tests the first Flow Error in the run method
def test_expand_cluster_with_detected_peers_error(patch_etcd_utils_read,
                                                  patch_cluster_load):
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "node_context"
    expand_cluster_with_detected_peers = ExpandClusterWithDetectedPeers()
    param = maps.NamedDict()
    param['TendrlContext.integration_id'] = "test_integration_id"
    param['Node[]'] = []
    param["job_id"] = ""
    param["flow_id"] = ""
    param['TendrlContext.sds_name'] = "test_sds"
    expand_cluster_with_detected_peers.parameters = param
    patch_cluster_load.return_value = MockObject().load()
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.Cluster = MockObject
    with pytest.raises(FlowExecutionFailedError):
        expand_cluster_with_detected_peers.run()
