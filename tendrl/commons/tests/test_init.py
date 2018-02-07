import __builtin__
import etcd
from etcd import Client
import importlib
import inspect
import maps
from mock import MagicMock
from mock import patch
import os
import pkgutil
import pytest
import yaml


from tendrl.commons import objects
import tendrl.commons.objects.node_context as node
from tendrl.commons import TendrlNS


@patch.object(etcd, "Client")
@patch.object(Client, "read")
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
    NS["config"] = maps.NamedDict()
    NS.config["data"] = maps.NamedDict()
    NS.config.data['tags'] = "test"
    tendrlNS = TendrlNS()
    return tendrlNS


def test_constructor():

    with patch.object(TendrlNS, 'setup_common_objects') as \
            mocked_method:
        mocked_method.return_value = None
        tendrlNS = TendrlNS()
    tendrlNS = init()
    # Default Parameter Testing
    assert tendrlNS.ns_name == "tendrl"
    assert tendrlNS.ns_src == "tendrl.commons"
    # Check for existance and right data type
    assert isinstance(NS, maps.NamedDict)


# Testing _list_modules_in_package_path
def test_list_modules_in_package_path():

    tendrlNS = init()
    modules = [
        ('alert',
         'tendrl.commons.objects.alert'),
        ('block_device',
         'tendrl.commons.objects.block_device'),
        ('cluster',
         'tendrl.commons.objects.cluster'),
        ('cluster_alert',
         'tendrl.commons.objects.cluster_alert'),
        ('cluster_alert_counters',
         'tendrl.commons.objects.cluster_alert_counters'),
        ('cluster_node_context',
         'tendrl.commons.objects.cluster_node_context'),
        ('cluster_tendrl_context',
         'tendrl.commons.objects.cluster_tendrl_context'),
        ('cpu', 'tendrl.commons.objects.cpu'),
        ('definition', 'tendrl.commons.objects.definition'),
        ('detected_cluster', 'tendrl.commons.objects.detected_cluster'),
        ('disk', 'tendrl.commons.objects.disk'),
        ('job', 'tendrl.commons.objects.job'),
        ('memory', 'tendrl.commons.objects.memory'),
        ('node', 'tendrl.commons.objects.node'),
        ('node_alert',
         'tendrl.commons.objects.node_alert'),
        ('node_alert_counters',
         'tendrl.commons.objects.notification_only_alert'),
        ('node_context', 'tendrl.commons.objects.node_context'),
        ('node_network', 'tendrl.commons.objects.node_network'),
        ('notification_only_alert',
         'tendrl.commons.objects.notification_only_alert'),
        ('os', 'tendrl.commons.objects.os'),
        ('platform', 'tendrl.commons.objects.platform'),
        ('service', 'tendrl.commons.objects.service'),
        ('tendrl_context', 'tendrl.commons.objects.tendrl_context'),
        ('virtual_disk', 'tendrl.commons.objects.virtual_disk')]
    ns_objects_path = os.path.join(os.path.dirname(os.path.abspath(__file__)).
                                   rsplit('/', 1)[0], "objects")
    ns_objects_prefix = "tendrl.commons.objects."
    ret = tendrlNS._list_modules_in_package_path(ns_objects_path,
                                                 ns_objects_prefix)

    # TO-DISCUSS : modules is hard coded and might change in future
    assert len(ret) == len(modules) + 1
    ret = tendrlNS._list_modules_in_package_path("test", "test")
    assert len(ret) == 0


# Testing _register_subclasses_to_ns
def test_register_subclasses_to_ns(monkeypatch):
    tendrlNS = init()
    tendrlNS._register_subclasses_to_ns()
    assert len(getattr(NS.tendrl, "objects")) > 0
    assert len(getattr(NS.tendrl, "flows")) > 0
    ns_objects_path = os.path.join(
        os.path.dirname(
            os.path.abspath(__file__)).rsplit(
            '/', 1)[0], "objects")
    ns_objects_prefix = "tendrl.commons.objects."
    modules = tendrlNS._list_modules_in_package_path(ns_objects_path,
                                                     ns_objects_prefix)

    for mode_name, mod_cls in modules:
        assert hasattr(NS.tendrl.objects, mode_name.title().replace('_', '')) \
            is True

    def list_package(self_obj, package_path, prefix):
        if "flows" in prefix:
            return [('ImportCluster', 'tendrl.commons.flows.import_cluster')]
        else:
            modules = []
            for importer, name, ispkg in pkgutil.walk_packages(
                    path=[package_path]):
                modules.append((name, prefix + name))
        return modules

    monkeypatch.setattr(TendrlNS, '_list_modules_in_package_path',
                        list_package)
    tendrlNS._register_subclasses_to_ns()
    assert len(getattr(NS.tendrl, "objects")) > 0


# Testing _add_object
def test_add_object():
    tendrlNS = init()
    obj_name = "test_obj"
    obj = importlib.import_module(
        "tendrl.commons.objects.cluster_node_context")
    current_ns = tendrlNS._get_ns()
    obj_cls = ""
    for obj_cls in inspect.getmembers(obj, inspect.isclass):
        tendrlNS._add_object(obj_name, obj_cls[1])
        break

    assert isinstance(getattr(current_ns.objects, "_test_obj")['atoms'],
                      maps.NamedDict)
    assert isinstance(getattr(current_ns.objects, "_test_obj")['flows'],
                      maps.NamedDict)
    with patch.object(TendrlNS, "_get_ns") as mock_add_obj:
        mock_add_obj.return_value = maps.NamedDict(
            objects=maps.NamedDict(_Service=maps.NamedDict(
                atoms=maps.NamedDict())))
        tendrlNS._add_object("Service", obj_cls[1])
    with patch.object(TendrlNS, "_get_ns") as mock_add_obj:
        mock_add_obj.return_value = maps.NamedDict(
            objects=maps.NamedDict(
                _Service=maps.NamedDict(
                    flows=maps.NamedDict())))
        tendrlNS._add_object("Service", obj_cls[1])


# Testing _get_objects
def test_get_objects():
    path = os.path.join(os.path.dirname(
                        os.path.dirname(os.path.abspath(__file__))), "objects")
    objects_list = [d.title().replace('_', '') for d in os.listdir(path)
                    if os.path.isdir(os.path.join(path, d))]
    tendrlNS = init()
    ret = tendrlNS._get_objects()
    assert isinstance(objects_list, list)
    assert ret is not None
    # TO-DISCUSS : object_list is hard coded and might change in future
    assert set(ret) == set(objects_list)


# Testing _get_object
def test_get_object():
    tendrlNS = init()
    ret = tendrlNS._get_object("NodeNetwork")
    assert (inspect.isclass(ret)) is True
    assert (issubclass(ret, objects.BaseObject)) is True
    path = os.path.join(os.path.dirname(os.path.dirname(
                        os.path.abspath(__file__))), "objects",
                        "definition")
    with open(os.path.join(path, "master.yaml"), 'r') as f:
        definition = yaml.safe_load(f)
    def_obj = definition["namespace.tendrl"]["objects"]["NodeNetwork"]["attrs"]
    # Creating instance of the class
    temp_instance = ret()
    # Comparing attributes of object from actual definition
    for k, v in def_obj.items():
        assert hasattr(temp_instance, k.lower())


# Testing _get_ns():
def test_get_ns():
    tendrlNS = init()
    assert isinstance(tendrlNS._get_ns(), maps.NamedDict) is True
    tendrlNS.ns_name = "integrations"
    tendrlNS._create_ns()
    assert isinstance(tendrlNS._get_ns(), maps.NamedDict) is True


# Testing get_obj_definition
def test_get_obj_definition():
    tendrlNS = init()
    ret = tendrlNS.get_obj_definition("Service")
    assert ret is not None
    assert isinstance(ret, maps.NamedDict) is True
    assert hasattr(ret, "attrs") is True
    NS["compiled_definitions"] = tendrlNS.current_ns.definitions
    ret = tendrlNS.get_obj_definition("Service")
    assert ret is not None
    assert isinstance(ret, maps.NamedDict) is True
    assert hasattr(ret, "attrs") is True


# Testing get_obj_flow_definition
def test_get_obj_flow_definition():
    tendrlNS = init()
    with pytest.raises(KeyError):
        tendrlNS.get_obj_flow_definition("Service", "test")


# Testing get_flow_definiiton()
def test_get_flow_definition():
    tendrlNS = init()
    with pytest.raises(KeyError):
        tendrlNS.get_flow_definition("BaseFlow")
    NS["compiled_definitions"] = tendrlNS.current_ns.definitions
    tendrlNS.get_flow_definition("ImportCluster")


# Testing get_atom_definition
def test_get_atom_definition():
    tendrlNS = init()
    ret = tendrlNS.get_atom_definition("Service", "CheckServiceStatus")
    assert ret is not None
    assert isinstance(ret, maps.NamedDict) is True
    assert hasattr(ret, "inputs") is True


# Testing add_atom
def test_add_atom():
    tendrlNS = init()
    obj_name = "Service"
    current_ns = tendrlNS._get_ns()
    obj = importlib.import_module(
        "tendrl.commons.objects.service.atoms.check_service_status")
    atom_class = ""
    for atom_cls in inspect.getmembers(obj, inspect.isclass):
        tendrlNS._add_atom(obj_name, "test_atom", atom_cls[1])
        atom_class = atom_cls[1]
        break
    assert hasattr(current_ns.objects["_Service"]['atoms'], "test_atom")
    assert current_ns.objects["_Service"]['atoms']["test_atom"] == atom_class


# Testing setup_definitions
def test_setup_definitions():
    tendrlNS = init()
    tendrlNS.setup_definitions()
    assert tendrlNS.current_ns is not None
    assert isinstance(tendrlNS.current_ns, maps.NamedDict) is True


# Testing add_flow
def test_add_flow():
    tendrlNS = init()
    flow_class = ""
    flow = importlib.import_module("tendrl.commons.flows.create_cluster")
    for flow_cls in inspect.getmembers(flow, inspect.isclass):
        tendrlNS._add_flow("test_flow", flow_cls[1])
        flow_class = flow_cls[1]
        break
    current_ns = tendrlNS._get_ns()
    assert hasattr(current_ns.flows, "test_flow") is True
    assert current_ns.flows["test_flow"] is flow_class


# Testing get_flow
def test_get_flow():
    tendrlNS = init()
    ret = tendrlNS.get_flow("ImportCluster")
    assert ret is not None


# Testing add_obj_flow
def test_add_obj_flow():
    tendrlNS = init()
    flow = importlib.import_module("tendrl.commons.flows")
    for flow_cls in inspect.getmembers(flow, inspect.isclass):
        tendrlNS._add_obj_flow("Node", "AtomExecutionFailedError", flow_cls[1])
        break
    ret = tendrlNS.get_obj_flow("Node", "AtomExecutionFailedError")
    assert ret is not None
    assert (inspect.isclass(ret)) is True


# Testing get_obj_flow
def test_get_obj_flow():
    tendrlNS = init()
    flow = importlib.import_module("tendrl.commons.flows")
    for flow_cls in inspect.getmembers(flow, inspect.isclass):
        tendrlNS._add_obj_flow("Node", "AtomExecutionFailedError", flow_cls[1])
        break
    ret = tendrlNS.get_obj_flow("Node", "AtomExecutionFailedError")
    assert ret is not None
    assert (inspect.isclass(ret)) is True


# Testing get_obj_flows
def test_get_obj_flows():
    tendrlNS = init()
    flow = importlib.import_module("tendrl.commons.flows")
    for flow_cls in inspect.getmembers(flow, inspect.isclass):
        tendrlNS._add_obj_flow("Node", "AtomExecutionFailedError", flow_cls[1])
        break
    ret = tendrlNS._get_obj_flows("Node")
    assert ret is not None
    assert isinstance(ret, maps.NamedDict)


# Testing get_atom
def test_get_atom():
    tendrlNS = init()
    ret = tendrlNS.get_atom("Node", "Cmd")
    assert ret is not None
    assert (inspect.isclass(ret)) is True


# Testing get_atoms
def test_get_atoms():
    tendrlNS = init()
    ret = tendrlNS._get_atoms("Node")
    assert ret is not None
    assert isinstance(ret, maps.NamedDict)


# Testing _create_ns()
def test_create_ns():
    tendrlNS = init()
    assert getattr(NS, "tendrl")
    tendrlNS.ns_name = "integrations"
    tendrlNS._create_ns()
    assert getattr(NS, "integrations")
    tendrlNS._create_ns()


# Testing_validate_ns_flow_definitions
def test_validate_ns_flow_definitions():
    tendrlNS = init()
    raw_ns = "namespace.tendrl"
    defs = tendrlNS.current_ns.definitions.get_parsed_defs()[raw_ns]
    defs["flows"]["test"] = maps.NamedDict()
    with pytest.raises(Exception):
        tendrlNS._validate_ns_flow_definitions(raw_ns, defs)
    tendrlNS.current_ns.flows["Test"] = "Test Flow"
    with pytest.raises(Exception):
        tendrlNS._validate_ns_flow_definitions(raw_ns, defs)
    tendrlNS.current_ns.flows = None
    defs = maps.NamedDict()
    tendrlNS._validate_ns_flow_definitions(raw_ns, defs)


# Testing _validate_ns_obj_definitions
def test_validate_ns_obj_definitions():
    tendrlNS = init()
    raw_ns = "namespace.tendrl"
    defs = tendrlNS.current_ns.definitions.get_parsed_defs()[raw_ns]
    defs_temp = defs
    defs_temp["objects"]["TestObject"] = maps.NamedDict()
    with pytest.raises(Exception):
        tendrlNS._validate_ns_obj_definitions(raw_ns, defs_temp)
    tendrlNS.current_ns.objects["_Node"]["atoms"]["Test"] =  \
        "Test atom class"
    with pytest.raises(Exception):
        tendrlNS._validate_ns_obj_definitions(raw_ns, defs)
    tendrlNS_temp = init()
    tendrlNS_temp.current_ns.objects["_Node"]["flows"]["Test"] = \
        "Test flow class"
    with pytest.raises(Exception):
        tendrlNS_temp._validate_ns_obj_definitions(raw_ns, defs)
    tendrlNS.current_ns.objects["Test"] = "Test Object"
    with pytest.raises(Exception):
        tendrlNS._validate_ns_obj_definitions(raw_ns, defs)
    tendrlNS_temp = init()
    defs = tendrlNS_temp.current_ns.definitions.get_parsed_defs()[raw_ns]
    defs["objects"]["Node"]["atoms"]["Test"] = \
        "Test atom class"
    with pytest.raises(Exception):
        tendrlNS_temp._validate_ns_obj_definitions(raw_ns, defs)
    defs = tendrlNS_temp.current_ns.definitions.get_parsed_defs()[raw_ns]
    defs["objects"]["Node"]["flows"] = maps.NamedDict()
    defs["objects"]["Node"]["flows"]["Test"] = "Test flow class"
    with pytest.raises(Exception):
        tendrlNS_temp._validate_ns_obj_definitions(raw_ns, defs)
    defs = maps.NamedDict()
    tendrlNS.current_ns.objects = None
    tendrlNS._validate_ns_obj_definitions(raw_ns, defs)


# Testing _validate_ns_definitions
def test_validate_ns_definitions():
    tendrlNS = init()
    tendrlNS._validate_ns_obj_definitions = MagicMock(return_value=None)
    tendrlNS._validate_ns_definitions()
    raw_ns = "namespace.tendrl"
    defs = tendrlNS.current_ns.definitions.get_parsed_defs()[raw_ns]
    tendrlNS._validate_ns_obj_definitions.assert_called_with(raw_ns, defs)
    tendrlNS._validate_ns_flow_definitions = MagicMock(return_value=None)
    tendrlNS._validate_ns_definitions()
    tendrlNS._validate_ns_flow_definitions.assert_called_with(raw_ns, defs)
    tendrlNS.current_ns.definitions = maps.NamedDict()
    with pytest.raises(Exception):
        tendrlNS._validate_ns_definitions()


# Testing setup_common_objects
def test_setup_common_objects(monkeypatch):
    tendrlNS = init()
    obj = importlib.import_module("tendrl.commons.tests.fixtures.config")
    for obj_cls in inspect.getmembers(obj, inspect.isclass):
        tendrlNS.current_ns.objects["Config"] = obj_cls[1]
    with patch.object(etcd, "Client", return_value=etcd.Client()) as client:
        tendrlNS.current_ns.objects.pop("NodeContext")
        tendrlNS.setup_common_objects()
        assert NS._int.client is not None
        assert NS._int.wclient is not None
        etcd.Client.assert_called_with(host=1, port=1)
        tendrlNS.current_ns.objects.pop("TendrlContext")
        tendrlNS.setup_common_objects()

    def client(**param):
        raise Exception
    monkeypatch.setattr(etcd, 'Client', client)
    with pytest.raises(Exception):
        tendrlNS.setup_common_objects()
