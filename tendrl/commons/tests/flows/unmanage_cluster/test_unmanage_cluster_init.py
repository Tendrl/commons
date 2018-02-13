import __builtin__
import etcd
import maps
import mock
from mock import patch
import pytest

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.unmanage_cluster import UnmanageCluster
from tendrl.commons import objects
from tendrl.commons.objects import AtomExecutionFailedError
from tendrl.commons.objects.cluster.atoms.is_cluster_managed \
    import IsClusterManaged
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS


def get_obj_definition(*args, **kwargs):
    ret = maps.NamedDict(
        {
            'attrs': {
                'integration_id': {
                    'type': 'String',
                    'help': 'Tendrl managed/generated cluster id for the sds'
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
    ret.flows["UnmanageCluster"] = {
        'help': 'Unmanage Cluster',
        'enabled': True,
        'type': 'test_type',
        'flows': {},
        'atoms': {},
        'inputs': 'test_input',
        'uuid': 'test_uuid'}
    return ret


def return_fail(param):
    return NS.tendrl.objects.Cluster(
        integration_id='13ced2a7-cd12-4063-bf6c-a8226b0789a0',
        status="unmanaging",
        is_managed='yes',
        locked_by={
            'job_id': "uuid"
        },
        current_job={
            'job_id': "uuid",
            'status': 'in_progress',
            'job_name': 'UnmanageCluster'
        }
    )


def return_pass(param):
    return NS.tendrl.objects.Cluster(
        integration_id='13ced2a7-cd12-4063-bf6c-a8226b0789a0',
        status=None,
        is_managed='yes',
        locked_by={}
    )


def read(key):
    if key == 'indexes/tags/tendrl/integration/None':
        raise etcd.EtcdKeyNotFound
    else:
        return maps.NamedDict(
            value=u'["bc15f88b-7118-485e-ab5c-cf4b9e1c2ee5"]'
        )


def save(*args):
    pass


@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
def init(patch_get_node_id, patch_read, patch_client):
    patch_get_node_id.return_value = 1
    patch_read.return_value = etcd.Client()
    patch_client.return_value = etcd.Client()
    setattr(__builtin__, "NS", maps.NamedDict())
    setattr(NS, "_int", maps.NamedDict())
    NS.type = "test"
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS._int.wclient = etcd.Client(**NS._int.etcd_kwargs)
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    NS.config.data['logging_socket_path'] = "test"
    NS.publisher_id = "node_context"
    NS.config.data['etcd_port'] = 8085
    NS.config.data['etcd_connection'] = "Test Connection"
    tendrlNS = TendrlNS()
    return tendrlNS


@mock.patch(
    'tendrl.commons.event.Event.__init__',
    mock.Mock(return_value=None)
)
@mock.patch(
    'tendrl.commons.message.Message.__init__',
    mock.Mock(return_value=None)
)
def test_run():
    init()
    param = maps.NamedDict()
    param['TendrlContext.integration_id'] = None
    with patch.object(TendrlNS, 'get_obj_definition', get_obj_definition):
        unmanage_cluster = UnmanageCluster(parameters=param)
    with patch.object(objects.BaseObject, 'load', return_fail):
        with patch.object(NS._int.client, 'read', read):
            with pytest.raises(FlowExecutionFailedError):
                unmanage_cluster.run()
    param['TendrlContext.integration_id'] = \
        '94ac63ba-de73-4e7f-8dfa-9010d9554084'
    unmanage_cluster._defs['pre_run'] = [
        'tendrl.objects.Cluster.atoms.IsClusterManaged'
    ]
    with patch.object(NS._int.client, 'read', read):
        with patch.object(objects.BaseObject, 'save', save):
            with patch.object(IsClusterManaged, 'run', return_value=True):
                with patch.object(objects.BaseObject, 'load', return_pass):
                    unmanage_cluster.run()
    with patch.object(NS._int.client, 'read', read):
        with patch.object(objects.BaseObject, 'save', save):
            with patch.object(IsClusterManaged, 'run', return_value=False):
                with patch.object(objects.BaseObject, 'load', return_pass):
                    with pytest.raises(AtomExecutionFailedError):
                        unmanage_cluster.run()
