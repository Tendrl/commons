import __builtin__
import importlib
import maps
import mock
import pytest

from mock import patch

import tendrl.commons.objects.cluster as cluster
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.expand_cluster import gluster_help
from tendrl.commons.objects.cluster import Cluster
from tendrl.commons.utils import etcd_utils


'''Unit Test Cases'''


def test_get_node_ips():
    param = maps.NamedDict()
    param["Cluster.node_configuration"] = {
        "test_node": maps.NamedDict(role="mon", provisioning_ip="test_ip")}
    ret = gluster_help.get_node_ips(param)
    assert ret[0] == "test_ip"


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@patch.object(etcd_utils, 'read')
@patch.object(cluster.Cluster, 'load')
def test_expand_gluster(patch_cluster_load, patch_etcd_utils_read):
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.publisher_id = "node_context"
    NS.tendrl = maps.NamedDict()
    NS.tendrl.objects = maps.NamedDict()
    NS.tendrl.objects.Cluster = Cluster
    NS.config = maps.NamedDict()
    NS.config.data = maps.NamedDict()
    NS.config.data['glusterfs_repo'] = "test_gluster"
    param = maps.NamedDict()
    param["job_id"] = "test_id"
    param["flow_id"] = "test_flow_id"
    param['TendrlContext.integration_id'] = "test_integration_id"
    param["Cluster.node_configuration"] = {
        "test_node": maps.NamedDict(role="mon", provisioning_ip="test_ip")}
    NS.gluster_provisioner = importlib.import_module(
        "tendrl.commons.tests.fixtures.plugin").Plugin()
    with pytest.raises(FlowExecutionFailedError):
        gluster_help.expand_gluster(param)
    NS.config.data['glusterfs_repo'] = "gluster"
    gluster_help.expand_gluster(param)
    param["Cluster.node_configuration"] = {
        "test_node": maps.NamedDict(role="mon", provisioning_ip="test")}
    patch_etcd_utils_read.return_value = maps.NamedDict(
        value='{"current_job": {"status": "finished", "job_id": "54adf1aa-7dcf-4d43-9ca3-fb5b5a9d6b05", "job_name": "ImportCluster"}, "status": "", "short_name": "t2", "volume_profiling_flag": "enable", "conf_overrides": "", "integration_id": "b7d4b5ae-d33d-49cf-ae6d-5d6bb494ece7", "errors": "[]", "node_configuration": "", "locked_by": {}, "last_sync": "2018-06-07 13:25:25.943914+00:00", "volume_profiling_state": "enabled", "public_network": "", "is_managed": "yes", "node_identifier": "[]", "cluster_network": "172.28.128.0/24"}')
    # patch_cluster_load.return_value = {"integration_id": "b7d4b5ae-d33d-49cf-ae6d-5d6bb494ece7", "current_job": {"status": "finished", "job_id": "54adf1aa-7dcf-4d43-9ca3-fb5b5a9d6b05", "job_name": "ImportCluster"}, "errors": "[]", "node_configuration": "", "short_name": "t2", "locked_by": {}, "last_sync": "2018-06-07 13:25:25.943914+00:00", "status": "", "volume_profiling_state": "enabled", "public_network": "", "is_managed": "yes", "node_identifier": "[]", "cluster_network": "172.28.128.0/24", "volume_profiling_flag": "enable", "conf_overrides": ""}
    gluster_help.expand_gluster(param)
