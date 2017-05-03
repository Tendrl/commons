import os
import pytest
import maps
import importlib
import inspect
import yaml
import __builtin__
from tendrl.commons import objects
from tendrl.commons import TendrlNS

#__init__() testing
def test_constructor():

    '''
    Testing for constructor involves checking if all needed variales are declared/
    initialized
    '''

    tendrlNS = TendrlNS()

    # Default Parameter Testing
    assert tendrlNS.ns_name == "tendrl"
    assert tendrlNS.ns_src == "tendrl.commons"
    #Check for existance and right data type
    assert isinstance(NS,maps.NamedDict)

#Testing _list_modules_in_package_path
def test_list_modules_in_package_path():

    tendrlNS = TendrlNS("tendrl","tendrl.commons")
    modules = [('cluster_node_context', 'tendrl.commons.objects.cluster_node_context'), ('cluster_tendrl_context', 'tendrl.commons.objects.cluster_tendrl_context'),\
              ('cpu', 'tendrl.commons.objects.cpu'),('definition', 'tendrl.commons.objects.definition'), ('detected_cluster', 'tendrl.commons.objects.detected_cluster'),\
              ('disk', 'tendrl.commons.objects.disk'), ('file','tendrl.commons.objects.file'), ('job','tendrl.commons.objects.job'),\
              ('memory', 'tendrl.commons.objects.memory'), ('node', 'tendrl.commons.objects.node'), ('node_context', 'tendrl.commons.objects.node_context'),\
              ('node_network', 'tendrl.commons.objects.node_network'), ('os', 'tendrl.commons.objects.os'), ('platform', 'tendrl.commons.objects.platform'),\
              ('service', 'tendrl.commons.objects.service'), ('tendrl_context', 'tendrl.commons.objects.tendrl_context')]
    ns_objects_path = os.path.join(os.path.dirname(os.path.abspath(__file__)).rsplit('/',1)[0],"objects")
    ns_objects_prefix = "tendrl.commons.objects."
    ret = tendrlNS._list_modules_in_package_path(ns_objects_path,ns_objects_prefix)

    #TO-DISCUSS : modules is hard coded and might change in future
    assert ret == modules
    ret = tendrlNS._list_modules_in_package_path("test","test")
    assert len(ret) == 0

#Testing _register_subclasses_to_ns
def test_register_subclasses_to_ns():
    tendrlNS = TendrlNS()
    tendrlNS._register_subclasses_to_ns()
    assert len(getattr(NS.tendrl,"objects")) > 0
    assert len(getattr(NS.tendrl,"flows")) > 0
    ns_objects_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),"objects")
    ns_objects_prefix = "tendrl.commons.objects."
    modules = tendrlNS._list_modules_in_package_path(ns_objects_path,ns_objects_prefix)
    for mode_name,mod_cls in modules:
        assert hasattr(NS.tendrl.objects,mode_name.title().replace('_','')) == True

#Testing _add_object
def test_add_object():
    tendrlNS = TendrlNS()
    obj_name = "test_obj"
    obj = importlib.import_module("tendrl.commons.objects.cluster_node_context")

    current_ns = tendrlNS._get_ns()
    for obj_cls in inspect.getmembers(obj, inspect.isclass):
        tendrlNS._add_object(obj_name,obj_cls[1])
        break

    assert isinstance(getattr(current_ns.objects,"_test_obj")['atoms'],maps.NamedDict)
    assert isinstance(getattr(current_ns.objects,"_test_obj")['flows'],maps.NamedDict)

#Testing _get_objects
def test_get_objects():
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"objects")
    objects_list = [d.title().replace('_','') for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
    tendrlNS = TendrlNS()
    ret = tendrlNS._get_objects()
    assert isinstance(objects_list,list)
    assert ret is not None
    #TO-DISCUSS : object_list is hard coded and might change in future
    assert set(ret) == set(objects_list)

#Testing _get_object
def test_get_object():
    tendrlNS = TendrlNS()
    ret = tendrlNS._get_object("NodeNetwork")
    assert (inspect.isclass(ret)) == True
    assert (issubclass(ret, objects.BaseObject)) == True
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"objects","definition")
    with open(os.path.join(path,"master.yaml"),'r') as f:
        definition = yaml.load(f)
    def_obj = definition["namespace.tendrl"]["objects"]["NodeNetwork"]["attrs"]
    #Creating instance of the class
    temp_instance = ret()
    #Comparing attributes of object from actual definition
    for k,v in def_obj.items():
        assert hasattr(temp_instance,k.lower())

#Testing _get_ns():
def test_get_ns():
    tendrlNS = TendrlNS()
    ret = tendrlNS._get_ns()
    assert isinstance(ret,maps.NamedDict) == True

#Testing get_obj_definition
def test_get_obj_definition():
    tendrlNS = TendrlNS()
    ret = tendrlNS.get_obj_definition("Service")
    assert ret != None
    assert isinstance(ret,maps.NamedDict) == True
    assert hasattr(ret,"attrs") == True

#Testing get_obj_flow_definition
def test_get_obj_flow_definition():
    tendrlNS = TendrlNS()
    with pytest.raises(KeyError):
        ret = tendrlNS.get_obj_flow_definition("Service","test")

#Testing get_flow_definiiton()
def test_get_flow_definition():
    tendrlNS = TendrlNS()
    with pytest.raises(KeyError):
        ret = tendrlNS.get_flow_definition("BaseFlow")

#Testing get_atom_definition
def test_get_atom_definition():
    tendrlNS = TendrlNS()
    ret = tendrlNS.get_atom_definition("Service","CheckServiceStatus")
    assert ret != None
    assert isinstance(ret,maps.NamedDict) == True
    assert hasattr(ret,"inputs") == True

#Testing add_atom
def test_add_atom():
    tendrlNS = TendrlNS()
    obj_name = "Service"
    current_ns = tendrlNS._get_ns()
    obj = importlib.import_module("tendrl.commons.objects.service.atoms.check_service_status")
    atom_class = ""
    for atom_cls in inspect.getmembers(obj,inspect.isclass):
        tendrlNS._add_atom(obj_name,"test_atom",atom_cls[1])
        atom_class = atom_cls[1]
        break
    assert hasattr(current_ns.objects["_Service"]['atoms'],"test_atom")
    assert current_ns.objects["_Service"]['atoms']["test_atom"] == atom_class

#Testing setup_definitions
def test_setup_definitions():
    tendrlNS = TendrlNS()
    tendrlNS.setup_definitions()
    assert tendrlNS.current_ns != None
    assert isinstance(tendrlNS.current_ns,maps.NamedDict) == True

#Testing add_flow
def test_add_flow():
    tendrlNS = TendrlNS()
    flow_class = ""
    flow = importlib.import_module("tendrl.commons.flows.create_cluster")
    for flow_cls in inspect.getmembers(flow, inspect.isclass):
        tendrlNS._add_flow("test_flow",flow_cls[1])
        flow_class = flow_cls[1]
        break
    current_ns = tendrlNS._get_ns()
    assert hasattr(current_ns.flows,"test_flow") == True
    assert current_ns.flows["test_flow"] == flow_class

#Testing get_flow
def test_get_flow():
    tendrlNS = TendrlNS()
    ret = tendrlNS.get_flow("ImportCluster")
    assert ret is not None

#Testing add_obj_flow
def test_add_obj_flow():
    tendrlNS = TendrlNS()
    flow = importlib.import_module("tendrl.commons.flows")
    for flow_cls in inspect.getmembers(flow,inspect.isclass):
        tendrlNS._add_obj_flow("Node","AtomExecutionFailedError",flow_cls[1])
        break
    ret = tendrlNS.get_obj_flow("Node","AtomExecutionFailedError")
    assert ret is not None
    assert (inspect.isclass(ret)) == True

#Testing get_obj_flow
def test_get_obj_flow():
    tendrlNS = TendrlNS()
    flow = importlib.import_module("tendrl.commons.flows")
    for flow_cls in inspect.getmembers(flow,inspect.isclass):
        tendrlNS._add_obj_flow("Node","AtomExecutionFailedError",flow_cls[1])
        break
    ret = tendrlNS.get_obj_flow("Node","AtomExecutionFailedError")
    assert ret is not None
    assert (inspect.isclass(ret)) == True

#Testing get_obj_flows
def test_get_obj_flows():
    tendrlNS = TendrlNS()
    flow = importlib.import_module("tendrl.commons.flows")
    for flow_cls in inspect.getmembers(flow,inspect.isclass):
        tendrlNS._add_obj_flow("Node","AtomExecutionFailedError",flow_cls[1])
        break
    ret = tendrlNS._get_obj_flows("Node")
    assert ret is not None
    assert isinstance(ret,maps.NamedDict)

#Testing get_atom
def test_get_atom():
    tendrlNS = TendrlNS()
    ret = tendrlNS.get_atom("Node","Cmd")
    assert ret is not None
    assert (inspect.isclass(ret)) == True

#Testing get_atoms
def test_get_atoms():
    tendrlNS = TendrlNS()
    ret = tendrlNS._get_atoms("Node")
    assert ret is not None
    assert isinstance(ret,maps.NamedDict)

#Testing _create_ns()
def test_create_ns():
    tendrlNS = TendrlNS()
    assert getattr(NS, "tendrl")

#Testing_validate_ns_flow_definitions 
def test_validate_ns_flow_definitions():
    tendrlNS = TendrlNS()
    raw_ns = "namespace.tendrl"
    defs = tendrlNS.current_ns.definitions.get_parsed_defs()[raw_ns]
    defs["flows"]["test"] = maps.NamedDict()
    with pytest.raises(Exception):
        tendrlNS._validate_ns_flow_definitions(raw_ns,defs)
    tendrlNS.current_ns.flows["Test"] = "Test Flow"
    with pytest.raises(Exception):
        tendrlNS._validate_ns_flow_definitions(raw_ns,defs)

#Testing _validate_ns_obj_definitions
def test_validate_ns_obj_definitions():
    tendrlNS = TendrlNS()
    raw_ns = "namespace.tendrl"
    defs = tendrlNS.current_ns.definitions.get_parsed_defs()[raw_ns]
    defs_temp = defs
    defs_temp["objects"]["TestObject"] = maps.NamedDict()
    with pytest.raises(Exception):
        tendrlNS._validate_ns_obj_definitions(raw_ns,defs_temp)
    tendrlNS.current_ns.objects["_Node"]["atoms"]["Test"] =  "Test atom class"
    with pytest.raises(Exception):
        tendrlNS._validate_ns_obj_definitions(raw_ns,defs_temp)
    tendrlNS_temp = TendrlNS()
    tendrlNS_temp.current_ns.objects["_Node"]["flows"]["Test"] = "Test flow class"
    with pytest.raises(Exception):
        tendrlNS_temp._validate_ns_obj_definitions(raw_ns,defs_temp)
    tendrlNS.current_ns.objects["Test"] = "Test Object"
    with pytest.raises(Exception):
        tendrlNS._validate_ns_obj_definitions(raw_ns,defs)

#Testing setup_comon_objects
def test_setup_common_objects():
    tendrlNS_config = TendrlNS()
    obj = importlib.import_module("tendrl.commons.fixtures.config")
    for obj_cls in inspect.getmembers(obj, inspect.isclass):
        tendrlNS_config.current_ns.objects["Config"] = obj_cls[1]
    with pytest.raises(AttributeError):
        tendrlNS_config.setup_common_objects()
    tendrlNS_NodeContext = TendrlNS()
    obj = importlib.import_module("tendrl.commons.fixtures.nodecontext")
    for obj_cls in inspect.getmembers(obj, inspect.isclass):
        tendrlNS_NodeContext.current_ns.objects["NodeContext"] = obj_cls[1]
    tendrlNS_NodeContext.setup_common_objects()
    assert tendrlNS_NodeContext.current_ns.node_context is not None
    assert isinstance(tendrlNS_NodeContext.current_ns.node_context,obj_cls[1])
    tendrlNS_TendrlContext = TendrlNS()
    obj = importlib.import_module("tendrl.commons.fixtures.tendrlcontext")
    for obj_cls in inspect.getmembers(obj, inspect.isclass):
        tendrlNS_TendrlContext.current_ns.objects["TendrlContext"] = obj_cls[1]
    tendrlNS_TendrlContext.setup_common_objects()
    assert tendrlNS_TendrlContext.current_ns.tendrl_context is not None
    assert isinstance(tendrlNS_TendrlContext.current_ns.tendrl_context,obj_cls[1])
