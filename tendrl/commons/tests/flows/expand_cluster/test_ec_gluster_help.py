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


class mock_plugin(object):
    def setup_gluster_node(self, node_ips, repo=None):
        return True

    def expand_gluster_cluster(self, node):
        return False


class mock_provisioner(object):
    def get_plugin(self):
        return mock_plugin()


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
        value='{"current_job": '
              '{"status": "finished",'
              '"job_id": "test_job_id",'
              '"job_name": "ImportCluster"'
              '},'
              '"status": "",'
              '"short_name": "t2",'
              '"volume_profiling_flag": "enable",'
              '"conf_overrides": "",'
              '"integration_id": "test_integration_id",'
              '"errors": "[]",'
              '"node_configuration": "",'
              '"locked_by": {},'
              '"last_sync": "2018-06-07 13:25:25.943914+00:00",'
              '"volume_profiling_state": "enabled",'
              '"public_network": "",'
              '"is_managed": "yes",'
              '"node_identifier": "[]",'
              '"cluster_network": "127.0.0.1/24"}'
    )
    gluster_help.expand_gluster(param)
    NS.gluster_provisioner = mock_provisioner()
    with pytest.raises(FlowExecutionFailedError):
        gluster_help.expand_gluster(param)
