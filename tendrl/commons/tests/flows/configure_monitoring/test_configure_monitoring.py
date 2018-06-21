import __builtin__
import maps
import pytest
from mock import patch

from tendrl.commons.flows.configure_monitoring import ConfigureMonitoring
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.utils import etcd_utils
from tendrl.commons.objects.cluster import Cluster

# basic flow attributes from test_flows_init.py
def get_obj_definition(*args, **kwargs):
    def_obj = maps.NamedDict(
        {
            'attrs': {
                'integration_id': {
                    'type': 'String',
                    'help': 'Tendrl managed/generated cluster id for the sds '
                            'being managed by Tendrl'},
                'cluster_name': {
                    'type': 'String',
                    'help': 'Name of the cluster'},
                'node_id': {
                    'type': 'String',
                    'help': 'Tendrl ID for the managed node'},
                'cluster_id': {
                    'type': 'String',
                    'help': 'UUID of the cluster'},
                'sds_version': {
                    'type': 'String',
                    'help': "Version of the Tendrl managed sds, eg: '3.2.1'"},
                'sds_name': {
                    'type': 'String',
                    'help': "Name of the Tendrl managed sds, eg: 'gluster'"}},
            'help': 'Tendrl context',
            'obj_list': '',
            'enabled': True,
            'obj_value': 'nodes/$NodeContext.node_id/TendrlContext',
            'flows': {},
            'atoms': {}})
    def_obj.flows["ImportCluster"] = {
        'help': 'Tendrl context',
        'enabled': True,
        'type': 'test_type',
        'flows': {},
        'atoms': {},
        'inputs': 'test_input',
        'uuid': 'test_uuid'}
    return def_obj

@patch.object(Cluster, 'load')		# simulates 'load' method for 'Cluster' object
@patch.object(etcd_utils, 'read')	# simulates 'read' method from 'etcd_utils'
def test_run_fail(patch_cluster_load, patch_etcd_utils_read):
	setattr(__builtin__, "NS", maps.NamedDict())
	setattr(NS, "_int", maps.NamedDict())
	NS.publisher_id = "node_context"
	NS.tendrl = maps.NamedDict()
	NS.tendrl_context = maps.NamedDict()
	NS.tendrl_context.integration_id = "test_integration_id"
	NS.tendrl.objects = maps.NamedDict()
	NS.tendrl.objects.Cluster = Cluster

	configure_obj = ConfigureMonitoring()

	# should fail: unmanaged cluster
	with pytest.raises(FlowExecutionFailedError):
		configure_obj.run()

@patch.object(Cluster, 'load')		# simulates 'load' method for 'Cluster' object 
@patch.object(etcd_utils, 'read')	# simulates 'read' method from 'etcd_utils'
def test_run_success(patch_cluster_load, patch_etcd_utils_read):
	setattr(__builtin__, "NS", maps.NamedDict())
	setattr(NS, "_int", maps.NamedDict())
	NS.publisher_id = "node_context"
	NS.tendrl = maps.NamedDict()
	NS.tendrl_context = maps.NamedDict()
	NS.tendrl_context.integration_id = "test_integration_id"
	NS.tendrl.objects = maps.NamedDict()
	NS.tendrl.objects.Cluster = Cluster

	# simulates 'read' op to force 'is_managed' branch
	patch_etcd_utils_read.return_value = maps.NamedDict(
		integration_id = "test_integration_id",
		is_managed = "yes"
	)

	configure_obj = ConfigureMonitoring()
	configure_obj._defs = get_obj_definition()	# object cannot do final initialization without this

	# should succeed: cluster is managed
	configure_obj.run()