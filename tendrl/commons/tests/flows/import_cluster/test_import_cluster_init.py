import __builtin__
import etcd
import maps
import mock
from mock import patch
import pytest

import tendrl.commons.objects.node_context as node

from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.import_cluster import ImportCluster
from tendrl.commons import objects
from tendrl.commons.objects.node.atoms.cmd import Cmd
from tendrl.commons import TendrlNS
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
    ret.flows["ImportCluster"] = {
        'help': 'Tendrl context',
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
        import_status='done',
        import_job_id='0f2381f0-e6e3-4cad-bb84-47c06cb46ffb'
    )


def return_pass(param):
    return NS.tendrl.objects.Cluster(
        integration_id='13ced2a7-cd12-4063-bf6c-a8226b0789a0',
        import_status='new',
        import_job_id=''
    )


def return_job(param):
    return NS.tendrl.objects.Job(
        job_id="sfdsdf",
        payload={'parent': "xxxx"}
    )


def read(key):
    if key == 'indexes/tags/tendrl/integration/None':
        raise etcd.EtcdKeyNotFound
    elif key == 'indexes/tags/tendrl/integration/' \
                '94ac63ba-de73-4e7f-8dfa-9010d9554084':
        node_ids = maps.NamedDict()
        node_ids['value'] = '["bc4cad92-b7e3-4c63-b820-a439db3a0516",' \
                            '"a71af0e5-5241-4856-9e9c-22627a466b8d"]'
        return node_ids
    else:
        return etcd.EtcdResult(node={'newKey': False,
                                     'raft_index': 449389,
                                     '_children': [{u'createdIndex': 1657,
                                                    u'modifiedIndex': 1657,
                                                    u'dir': True,
                                                    u'key': u'/clusters/'
                                                            u'b7d4b5ae-d33d-'
                                                            u'49cf-ae6d-5d6bb'
                                                            u'494ece7'}
                                                   ],
                                     'createdIndex': 1657,
                                     'modifiedIndex': 1657,
                                     'value': None,
                                     'etcd_index': 101021,
                                     'expiration': None,
                                     'key': u'/clusters',
                                     'ttl': None,
                                     'action': u'get',
                                     'dir': True
                                     })


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
    NS._int.etcd_kwargs = {
        'port': 1,
        'host': 2,
        'allow_reconnect': True}
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS._int.wclient = etcd.Client(**NS._int.etcd_kwargs)
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
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


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
def test_run():
    init()
    param = maps.NamedDict()
    param['TendrlContext.integration_id'] = None
    param['Cluster.volume_profiling_flag'] = 'yes'
    with patch.object(TendrlNS, 'get_obj_definition', get_obj_definition):
        import_cluster = ImportCluster(parameters=param)
    with patch.object(objects.BaseObject, 'load', return_fail):
        with patch.object(NS._int.client, 'read', read):
            with patch.object(etcd_utils, 'read', read):
                with pytest.raises(FlowExecutionFailedError):
                    import_cluster.run()
    param['TendrlContext.integration_id'] = \
        '94ac63ba-de73-4e7f-8dfa-9010d9554084'
    import_cluster._defs['pre_run'] = ['tendrl.objects.Node.atoms.Cmd']
    with patch.object(NS._int.client, 'read', read):
        with patch.object(objects.BaseObject, 'save', save):
            with patch.object(Cmd, 'run', return_value=True):
                with patch.object(etcd_utils, 'read', read):
                    with patch.object(
                        NS.tendrl.objects.Cluster,
                        'load',
                        return_pass
                    ):
                        with patch.object(
                            NS.tendrl.objects.Job,
                            'load',
                            return_job
                        ):
                            import_cluster.run()
    with patch.object(NS._int.client, 'read', read):
        with patch.object(objects.BaseObject, 'save', save):
            with patch.object(Cmd, 'run', return_value=False):
                with patch.object(objects.BaseObject, 'load', return_pass):
                    with pytest.raises(FlowExecutionFailedError):
                        import_cluster.run()
