import __builtin__
import maps
import mock
from mock import patch

import etcd
from etcd import Client

from tendrl.commons.objects.cluster_node_context import ClusterNodeContext
from tendrl.commons.tests.fixtures.nodecontext import NodeContext
from tendrl.commons.utils import etcd_utils
from tendrl.commons.objects.cluster import Cluster

def load(*args):
	node_context = maps.NamedDict()
	node_context.machine_id = "Test machine id"
	node_context.node_id = 1
	node_context.fqdn = "Test fqdn"
	node_context.tags = ["test_tag1", "test_tag2"]
	node_context.status = True
	node_context.sync_status = True
	node_context.last_sync = "test_last_sync"
	return node_context

# Testing __init__
def test_constructor(monkeypatch):
	'''Testing for constructor involves checking if all needed

	variables are declared initialized
	'''
	setattr(__builtin__, "NS", maps.NamedDict())
	monkeypatch.setattr(NodeContext, 'load', load)
	NS.tendrl = maps.NamedDict()
	NS.tendrl.objects = maps.NamedDict()
	NS.tendrl.objects.NodeContext = NodeContext

	cluster_node_context = ClusterNodeContext(ipv4_addr="127.0.0.1")
	assert cluster_node_context.status
	cluster_node_context = ClusterNodeContext(ipv4_addr="127.0.0.1")
	assert cluster_node_context.node_id == 1


# Testing render
def test_render(monkeypatch):
	setattr(__builtin__, "NS", maps.NamedDict())
	monkeypatch.setattr(NodeContext, 'load', load)
	NS.tendrl = maps.NamedDict()
	NS.tendrl.objects = maps.NamedDict()
	NS.tendrl.objects.NodeContext = NodeContext

	NS.tendrl_context = maps.NamedDict()
	NS.tendrl_context.integration_id = 1
	cluster_node_context = ClusterNodeContext(ipv4_addr="127.0.0.1")
	assert cluster_node_context.render() is not None

# Testing save
@patch.object(Cluster, 'load')			# simulates 'load' method for 'Cluster' object 
@patch.object(etcd_utils, 'read')		# simulates 'read' method from 'etcd_utils'
@patch.object(etcd_utils, 'write')		# simulates 'write' method from 'etcd_utils'
@patch.object(etcd_utils, 'refresh')	# simulates 'refresh' method from 'etcd_utils'
def test_save(patch_cluster_load, patch_etcd_utils_read, patch_etcd_utils_write, patch_etcd_utils_refresh, monkeypatch):
	setattr(__builtin__, "NS", maps.NamedDict())
	setattr(NS, "_int", maps.NamedDict())
	monkeypatch.setattr(NodeContext, 'load', load)
	NS.tendrl = maps.NamedDict()
	NS.tendrl_context = maps.NamedDict()
	NS.tendrl_context.integration_id = "test_integration_id"
	NS.tendrl.objects = maps.NamedDict()
	NS.tendrl.objects.NodeContext = NodeContext
	NS._int.watchers = maps.NamedDict()

	cluster_node_context = ClusterNodeContext(ipv4_addr="127.0.0.1")

	# Test with ttl
	cluster_node_context.save(ttl="test")
	# Test without ttl
	cluster_node_context.save()