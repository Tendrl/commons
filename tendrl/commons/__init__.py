__version__ = '1.2'

import importlib
import inspect
import pkgutil


import namespaces as ns

from tendrl.commons import etcdobj
from tendrl.commons import flows
from tendrl.commons import log
from tendrl.commons import objects
from tendrl.commons.objects import atoms


class CommonNS(object):
    def __init__(self):
        super(CommonNS, self).__init__()
        import __builtin__
        setattr(__builtin__, "tendrl_ns", self)

        self.ns_str = self.to_str.split(".")[-1]
        # Create the component namespace
        setattr(self, self.ns_str,
                ns.Namespace(objects=ns.Namespace(), flows=ns.Namespace()))
        self.register_subclasses_to_ns()

        ns_obj = getattr(self, self.ns_str)
        # Definitions
        self.definitions = ns_obj.objects.Definition()

        # Config
        self.config = ns_obj.objects.Config()

        # etcd_orm
        etcd_kwargs = {'port': self.config.data['etcd_port'],
                       'host': self.config.data["etcd_connection"]}
        self.etcd_orm = etcdobj.Server(etcd_kwargs=etcd_kwargs)

        # NodeContext
        self.node_context = ns_obj.objects.NodeContext()

        self.tendrl_context = ns_obj.objects.TendrlContext()

        log.setup_logging(
            self.config.data['log_cfg_path'],
        )

    def get_ns(self):
        # eg: input : "tendrl.node_agent", return: "node_agent"
        return getattr(self, self.ns_str)

        # Create the "tendrl_ns.node_agent.objects.$obj.{atoms, flows} NS
    def add_object(self, name, obj_class):
        # obj is the actual instance of that Tendrl object
        # name of object as defined in Tendrl definitions
        self.get_ns().objects[name] = obj_class

        # This is to link atoms and flows (insdie obj) to the obj ns
        private_name = "_" + name
        self.get_ns().objects[private_name] = ns.Namespace()

        if 'atoms' not in self.get_ns().objects[private_name]:
            self.get_ns().objects[private_name]['atoms'] = ns.Namespace()

        if "flows" not in self.get_ns().objects[private_name]:
            self.get_ns().objects[private_name]['flows'] = ns.Namespace()

    def get_object(self, name):
        return self.get_ns().objects[name]

    def get_atom(self, obj_name, atom_name):
        private_name = "_" + obj_name
        return self.get_ns().objects[private_name]['atoms'][atom_name]

    def get_obj_flow(self, obj_name, flow_name):
        private_name = "_" + obj_name
        return self.get_ns().objects[private_name]['flows'][flow_name]

    def add_atom(self, obj_name, atom_name, atom_class):
        private_name = "_" + obj_name
        self.get_ns().objects[private_name]['atoms'][atom_name] = atom_class
        atom_class.obj = self.get_object(obj_name)

    def add_obj_flow(self, obj_name, flow_name, flow_class):
        private_name = "_" + obj_name
        self.get_ns().objects[private_name]['flows'][flow_name] = flow_class
        flow_class.obj = self.get_object(obj_name)

    def add_flow(self, name, flow_class):
        # flow is the actual instance of that Tendrl flow
        # name of object as defined in Tendrl definitions
        self.get_ns().flows[name] = flow_class

    def get_flow(self, name):
        return self.get_ns().flows[name]

    def register_subclasses_to_ns(self):
        # registers all subclasses of BaseObject, BaseFlow, BaseAtom to
        # tendrl_ns
        ns_root = importlib.import_module(self.to_str).__path__[0]

        # register objects and atoms, flows inside the objects
        ns_objects_path = ns_root + "/objects"
        ns_objects_prefix = self.to_str + ".objects."
        objs = self._list_modules_in_package_path(ns_objects_path,
                                                  ns_objects_prefix)
        for name, obj_fqdn in objs:
            obj = importlib.import_module(obj_fqdn)
            for obj_cls in inspect.getmembers(obj, inspect.isclass):
                if issubclass(obj_cls[1], objects.BaseObject):
                    obj_name = obj_cls[0]
                    self.add_object(obj_name, obj_cls[1])

                    ns_object_atoms_path = obj.__path__[0] + "/atoms"
                    ns_object_atoms_prefix = obj_fqdn + ".atoms."
                    for atom_name, atom_fqdn in \
                        self._list_modules_in_package_path(
                            ns_object_atoms_path,
                            ns_object_atoms_prefix):
                        atom = importlib.import_module(atom_fqdn)

                        for atom_cls in inspect.getmembers(atom,
                                                           inspect.isclass):
                            if issubclass(atom_cls[1], atoms.BaseAtom):
                                self.add_atom(atom_cls[1].obj.__name__,
                                              atom_cls[1].__name__,
                                              atom_cls[1])

                    ns_object_flows_path = obj.__path__[0] + "/flows"
                    ns_object_flows_prefix = obj_fqdn + ".flows."
                    for flow_name, flow_fqdn in \
                        self._list_modules_in_package_path(
                            ns_object_flows_path,
                            ns_object_flows_prefix):
                        flow = importlib.import_module(flow_fqdn)

                        for flow_cls in inspect.getmembers(flow,
                                                           inspect.isclass):
                            if issubclass(flow_cls[1], flows.BaseFlow):
                                self.add_obj_flow(flow_cls[1].obj.__name__,
                                                  flow_cls[1].__name__,
                                                  flow_cls[1])

        ns_flows_path = ns_root + "/flows"
        ns_flows_prefix = self.to_str + ".flows."
        flowz = self._list_modules_in_package_path(ns_flows_path,
                                                   ns_flows_prefix)
        for name, flow_fqdn in flowz:
            the_flow = importlib.import_module(flow_fqdn)
            for flow_cls in inspect.getmembers(the_flow, inspect.isclass):
                if issubclass(flow_cls[1], flows.BaseFlow):
                    self.add_flow(flow_cls[0], flow_cls[1])

    def _list_modules_in_package_path(self, package_path, prefix):
        modules = []
        for importer, name, ispkg in pkgutil.walk_packages(
                path=[package_path]):
            modules.append((name, prefix + name))
        return modules
