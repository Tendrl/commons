import __builtin__
import etcd
import maps
import mock
from mock import patch
import pytest

from tendrl.commons import objects
from tendrl.commons import TendrlNS

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.unmanage_cluster import UnmanageCluster
from tendrl.commons.objects.cluster.atoms.is_cluster_managed \
    import IsClusterManaged
import tendrl.commons.objects.node_context as node
from tendrl.commons.utils import etcd_utils


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


def return_cluster(param):
    return NS.tendrl.objects.Cluster(
        integration_id='13ced2a7-cd12-4063-bf6c-a8226b0789a0',
        status=None,
        is_managed='yes',
        locked_by={}
    )


def save_cluster(*args):
    pass


def return_job(param):
    return maps.NamedDict({
        "status": "in_progress",
        "valid_until": "",
        "errors": "",
        "job_id": "parent_job",
        "locked_by": {
            "node_id": "test_node_1",
            "type": "node",
            "fqdn": "",
            "tags": ["tendrl/integration/monitoring",
                     "tendrl/node_28c93b1d-361c-4b32-acc0-f405d2a05eca",
                     "tendrl/central-store", "tendrl/server", "tendrl/monitor",
                     "tendrl/node"]
        },
        "children": ["job_1",
                     "job_2",
                     "job_3",
                     "job_4",
                     "job_5"],
        "timeout": "yes",
        "output": {},
        "payload": {
            "status": "in_progress",
            "username": "admin",
            "run": "tendrl.flows.UnmanageCluster",
            "name": "UnmanageCluster",
            "parameters": {
                "TendrlContext.integration_id":
                    "94ac63ba-de73-4e7f-8dfa-9010d9554084",
                "cluster_id": "94ac63ba-de73-4e7f-8dfa-9010d9554084"
            },
            "tags": ["tendrl/monitor"],
            "created_at": "2018-06-11T07:21:52Z",
            "created_from": "API",
            "type": "node"
        }
    })


def save_job(*args):
    pass


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
@patch.object(etcd_utils, 'read')
def init(patch_etcd_utils_read,
         patch_get_node_id,
         patch_read,
         patch_client):
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
    patch_etcd_utils_read.return_value = maps.NamedDict(
        value='{"status": "UP",'
              '"pkey": "tendrl-node-test",'
              '"node_id": "test_node_id",'
              '"ipv4_addr": "test_ip",'
              '"tags": "[\\"my_tag\\"]",'
              '"sync_status": "done",'
              '"locked_by": "fd",'
              '"fqdn": "tendrl-node-test",'
              '"last_sync": "date"}')
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
        with patch.object(NS.tendrl.objects.Cluster, 'save', save_cluster):
            with patch.object(NS.tendrl.objects.Job, 'save', save_job):
                with patch.object(IsClusterManaged, 'run', return_value=True):
                    with patch.object(NS.tendrl.objects.Cluster,
                                      'load',
                                      return_cluster):
                        with patch.object(NS.tendrl.objects.Job,
                                          'load',
                                          return_job):
                            unmanage_cluster.run()
    with patch.object(NS._int.client, 'read', read):
        with patch.object(objects.BaseObject, 'save', save):
            with patch.object(IsClusterManaged, 'run', return_value=False):
                with patch.object(objects.BaseObject, 'load', return_pass):
                    with pytest.raises(FlowExecutionFailedError):
                        unmanage_cluster.run()
