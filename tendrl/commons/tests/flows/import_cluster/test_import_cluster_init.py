import __builtin__
import etcd
import importlib
import maps
import mock
from mock import patch
import pytest
import tempfile


from tendrl.commons.flows.create_cluster import utils as create_cluster_utils
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.import_cluster import ImportCluster
from tendrl.commons import objects
from tendrl.commons.objects.node.atoms.cmd import Cmd
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS
from tendrl.commons.tests.fixtures.client import Client
from tendrl.commons.utils import ansible_module_runner


'''Dummy Functions'''


def ansible_run(*args):
    if args[0]:
        return {"msg": "test_msg", "rc": 0}, "Error"
    else:
        return {"msg": "test_msg", "rc": 1}, "Error"


def read_failed(*args, **kwargs):
    if args[0]:
        if args[1] == 'nodes/TestNode/TendrlContext/integration_id':
            return maps.NamedDict(value="")
        else:
            return maps.NamedDict(value="failed")


def read_passed(*args, **kwargs):
    if args[0]:
        if args[1] == 'nodes/TestNode/TendrlContext/integration_id':
            return maps.NamedDict(value="")
        else:
            return maps.NamedDict(value="finished")


def read(*args, **kwargs):
    raise etcd.EtcdKeyNotFound


def open(*args, **kwargs):
    f = tempfile.TemporaryFile()
    return f


def run(*args):
    raise ansible_module_runner.AnsibleExecutableGenerationFailed


def load_trendrl_context(*args):
    ret = importlib.import_module(
        "tendrl.commons.tests.fixtures.client").Client()
    ret.detected_cluster_id = 'Test Cluster Id'
    ret.sds_pkg_version = '9.9'
    ret.detected_cluster_name = "Test Cluster name"
    ret.sds_pkg_name = "Test/package/name"
    ret.machine_id = "Test_machine_id"
    ret.fqdn = "fqdn"
    ret.tags = ["Test tag", "ceph/mon"]
    ret.status = True
    ret.node_id = 1
    ret.sync_status = True
    ret.last_sync = "test_last_sync"
    return ret


def load_tendrl_context_high_version(*args):
    ret = importlib.import_module(
        "tendrl.commons.tests.fixtures.client").Client()
    ret.detected_cluster_id = 'Test Cluster Id'
    ret.sds_pkg_version = '10.10'
    ret.detected_cluster_name = "Test Cluster name"
    ret.sds_pkg_name = "Test/package/name"
    ret.machine_id = "Test_machine_id"
    ret.fqdn = "fqdn"
    ret.tags = ["Test tag", "ceph/mon"]
    ret.status = True
    ret.node_id = 1
    return ret


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


def save(*args):
    raise Exception


'''Unit Test Cases'''


@patch.object(etcd, "Client")
@patch.object(etcd.Client, "read")
@patch.object(node.NodeContext, '_get_node_id')
def init(patch_get_node_id, patch_read, patch_client):
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
    tendrlNS = TendrlNS()
    return tendrlNS


@mock.patch('tendrl.commons.event.Event.__init__',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.message.Message.__init__',
            mock.Mock(return_value=None))
@mock.patch('gevent.sleep',
            mock.Mock(return_value=True))
@mock.patch('tendrl.commons.flows.create_cluster.utils.acquire_node_lock',
            mock.Mock(return_value=None))
@mock.patch('tendrl.commons.flows.create_cluster.utils.release_node_lock',
            mock.Mock(return_value=None))
def test_run():
    tendrlNS = init()
    param = maps.NamedDict()
    param['TendrlContext.integration_id'] = None
    param['Node[]'] = []
    with patch.object(TendrlNS, 'get_obj_definition', get_obj_definition):
        import_cluster = ImportCluster(parameters=param)
    with pytest.raises(FlowExecutionFailedError):
        import_cluster.run()
    param['TendrlContext.integration_id'] = "Test integration_id"
    param['DetectedCluster.sds_pkg_name'] = "Test package_name"
    param['Node[]'] = ["TestNode"]
    with patch.object(TendrlNS, 'get_obj_definition', get_obj_definition):
        import_cluster = ImportCluster(parameters=param)
    import_cluster._defs['pre_run'] = ['tendrl.objects.Node.atoms.Cmd']
    with patch.object(Cmd, 'run', return_value=True):
        with pytest.raises(FlowExecutionFailedError):
            import_cluster.run()
    NS.compiled_definitions = tendrlNS.current_ns.definitions
    NS._int.client = importlib.import_module(
        "tendrl.commons.tests.fixtures.client").Client()
    NS.config.data['package_source_type'] = "test"
    with patch.object(Cmd, 'run', return_value=True):
        with patch.object(Client, "read", read):
            with pytest.raises(FlowExecutionFailedError):
                import_cluster.run()
    NS.config.data['logging_socket_path'] = "test"
    with patch.object(Cmd, 'run', return_value=True):
        with patch.object(Client, "read") as mock_read:
            mock_read.return_value = maps.NamedDict(value="")
            with patch.object(objects.BaseObject, 'load',
                              load_trendrl_context):
                import_cluster.run()
        with patch.object(Client, "read", read_failed):
            param['DetectedCluster.sds_pkg_name'] = "gluster"
            with patch.object(objects.BaseObject, 'load',
                              load_trendrl_context):
                NS.config.data['package_source_type'] = 'rpm'
                with patch.object(ansible_module_runner.AnsibleRunner,
                                  'run', ansible_run):
                    with patch.object(create_cluster_utils,
                                      'gluster_create_ssh_setup_jobs',
                                      return_value=[1, 2]):
                        with pytest.raises(FlowExecutionFailedError):
                            import_cluster.run()
        NS.tendrl_context = importlib.import_module(
            "tendrl.commons.objects.tendrl_context").TendrlContext()
        NS.node_context = Client()
        NS.node_context.node_id = 1
        param['Node[]'] = ["TestNode", "Test_node"]
        param["import_after_expand"] = True
        param['DetectedCluster.sds_pkg_name'] = "test/package/name"
        with patch.object(TendrlNS, 'get_obj_definition', get_obj_definition):
            cluster_obj = ImportCluster(parameters=param)
        with patch.object(TendrlNS, 'get_atom_definition', get_obj_definition):
            cluster_obj._defs['pre_run'] = ['tendrl.objects.Node.atoms.Cmd']
            with patch.object(Client, 'load', load_trendrl_context):
                with patch.object(objects.BaseObject, 'load',
                                  load_trendrl_context):
                    with mock.patch('tendrl.commons.objects.__init__',
                                    mock.Mock(return_value=None)):
                        with mock.patch('tendrl.commons.objects.job.Job.save',
                                        mock.Mock(return_value=None)):
                            with patch.object(__builtin__, 'open',
                                              return_value=False):
                                cluster_obj.run()
        param['DetectedCluster.sds_pkg_name'] = "ceph"
        param['Node[]'] = ["TestNode"]
        with patch.object(TendrlNS, 'get_obj_definition', get_obj_definition):
            cluster_obj = ImportCluster(parameters=param)
        with patch.object(TendrlNS, 'get_atom_definition', get_obj_definition):
            cluster_obj._defs['pre_run'] = ['tendrl.objects.Node.atoms.Cmd']
            with patch.object(Client, 'load', load_trendrl_context):
                with patch.object(objects.BaseObject, 'load',
                                  load_trendrl_context):
                    with mock.patch('tendrl.commons.objects.__init__',
                                    mock.Mock(return_value=None)):
                        with mock.patch('tendrl.commons.objects.job.Job.save',
                                        mock.Mock(return_value=None)):
                            with patch.object(__builtin__, 'open', open):
                                with pytest.raises(FlowExecutionFailedError):
                                    cluster_obj.run()

        param['Node[]'] = ["TestNode"]
        param["import_after_expand"] = False
        param['DetectedCluster.sds_pkg_name'] = "gluster"
        with patch.object(Client, "read", read_passed):
            param['DetectedCluster.sds_pkg_name'] = "gluster"
            with patch.object(objects.BaseObject, 'load',
                              load_trendrl_context):
                with patch.object(Client, 'load', load_trendrl_context):
                    NS.config.data['package_source_type'] = 'rpm'
                    with patch.object(ansible_module_runner.AnsibleRunner,
                                      'run', ansible_run):
                        with patch.object(create_cluster_utils,
                                          'gluster_create_ssh_setup_jobs',
                                          return_value=[1, 2]):
                            with patch.object(
                                    ansible_module_runner.AnsibleRunner,
                                    'run', run):
                                with patch.object(create_cluster_utils,
                                                  'install_gdeploy',
                                                  return_value=False):
                                    with patch.object(create_cluster_utils,
                                                      'install_python_gdeploy',
                                                      return_value=False):
                                        import_cluster.run()
