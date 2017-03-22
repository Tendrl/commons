__version__ = '1.2.1'

import __builtin__
import importlib
import inspect
import logging
import pkgutil

import maps

from tendrl.commons import etcdobj
from tendrl.commons import flows
from tendrl.commons import log
from tendrl.commons import objects
from tendrl.commons.objects import BaseAtom

LOG = logging.getLogger(__name__)


class TendrlNS(object):
    def __init__(self, ns_name="tendrl", ns_src="tendrl.commons"):
        super(TendrlNS, self).__init__()
        if not hasattr(__builtin__, "NS"):
            setattr(__builtin__, "NS", maps.NamedDict())
        LOG.info("Creating namespace.%s from source %s", ns_name, ns_src)
        self.ns_name = ns_name
        self.ns_src = ns_src

        self._create_ns()

        self.current_ns = self._get_ns()
        LOG.info("namespace.%s created!", self.ns_name)
        self._register_subclasses_to_ns()

        self.setup_definitions()
        self.setup_common_objects()

    def setup_definitions(self):
        LOG.info("Setup Definitions for namespace.%s", self.ns_name)
        self.current_ns.definitions = self.current_ns.objects.Definition()

    def setup_common_objects(self):
        # Config, if the namespace has implemented its own Config object
        if "Config" in self.current_ns.objects:
            LOG.info("Setup Config for namespace.%s", self.ns_name)
            self.current_ns.config = self.current_ns.objects.Config()
            NS.config = self.current_ns.config

            # etcd_orm
            etcd_kwargs = {'port': self.current_ns.config.data['etcd_port'],
                           'host': self.current_ns.config.data[
                               "etcd_connection"]}
            LOG.info("Setup Etcd Orm for namespace.%s", self.ns_name)
            NS.etcd_orm = etcdobj.Server(etcd_kwargs=etcd_kwargs)
            log.setup_logging(self.current_ns.config.data['log_cfg_path'])

        # NodeContext, if the namespace has implemented its own
        if "NodeContext" in self.current_ns.objects:
            LOG.info("Setup NodeContext for namespace.%s", self.ns_name)

            self.current_ns.node_context = \
                self.current_ns.objects.NodeContext()
            NS.node_context = self.current_ns.node_context

        # TendrlContext, if the namespace has implemented its own
        if "TendrlContext" in self.current_ns.objects:
            LOG.info("Setup TendrlContext for namespace.%s", self.ns_name)
            self.current_ns.tendrl_context = \
                self.current_ns.objects.TendrlContext()
            NS.tendrl_context = self.current_ns.tendrl_context

    def _create_ns(self):
        ns_map = maps.NamedDict(objects=maps.NamedDict(),
                                flows=maps.NamedDict(),
                                ns=self)
        self.ns_str = self.ns_name.split(".")[-1]

        if 'integrations' in self.ns_name:
            if not hasattr(NS, "integrations"):
                setattr(NS, "integrations",
                        maps.NamedDict())
            setattr(NS.integrations, self.ns_str, ns_map)
        else:
            # Create the component namespace
            setattr(NS, self.ns_str, ns_map)

    def _get_ns(self):
        # eg: input : "tendrl.node_agent", return: "node_agent"
        if "integrations" in self.ns_name:
            return getattr(NS.integrations, self.ns_str)
        else:
            return getattr(NS, self.ns_str)

    def _add_object(self, name, obj_class):
        # obj is the actual instance of that Tendrl object
        # name of object as defined in Tendrl definitions
        obj_class._ns = self
        self.current_ns.objects[name] = obj_class

        # This is to link atoms and flows (insdie obj) to the obj ns
        private_name = "_" + name
        self.current_ns.objects[private_name] = maps.NamedDict()

        if 'atoms' not in self._get_ns().objects[private_name]:
            self.current_ns.objects[private_name]['atoms'] = maps.NamedDict()

        if "flows" not in self._get_ns().objects[private_name]:
            self.current_ns.objects[private_name]['flows'] = maps.NamedDict()

    def _get_object(self, name):
        return self.current_ns.objects[name]

    def get_atom(self, obj_name, atom_name):
        private_name = "_" + obj_name
        if private_name in self.current_ns.objects:
            self.current_ns.objects[private_name]['atoms'][atom_name]
        else:
            return NS.tendrl.objects[private_name]['atoms'][atom_name]
        #return self.current_ns.objects[private_name]['atoms'][atom_name]

    def get_obj_flow(self, obj_name, flow_name):
        private_name = "_" + obj_name
        return self.current_ns.objects[private_name]['flows'][flow_name]

    def _add_atom(self, obj_name, atom_name, atom_class):
        atom_class._ns = self
        private_name = "_" + obj_name
        self.current_ns.objects[private_name]['atoms'][atom_name] = atom_class
        atom_class.obj = self._get_object(obj_name)

    def _add_obj_flow(self, obj_name, flow_name, flow_class):
        flow_class._ns = self
        private_name = "_" + obj_name
        self.current_ns.objects[private_name]['flows'][flow_name] = flow_class
        flow_class.obj = self._get_object(obj_name)

    def _add_flow(self, name, flow_class):
        flow_class._ns = self
        # flow is the actual instance of that Tendrl flow
        # name of object as defined in Tendrl definitions
        self.current_ns.flows[name] = flow_class

    def get_flow(self, name):
        return self.current_ns.flows[name]

    def get_obj_definition(self, obj_name):
        raw_ns = "namespace.%s" % self.ns_name
        if hasattr(NS, "compiled_definitions"):
            raw_obj = NS.compiled_definitions.get_parsed_defs()[raw_ns][
                'objects'][obj_name]
        else:
            raw_obj = self.current_ns.definitions.get_parsed_defs()[raw_ns][
                'objects'][obj_name]

        return maps.NamedDict(attrs=raw_obj['attrs'],
                              enabled=raw_obj['enabled'],
                              obj_list=raw_obj.get('list', ""),
                              obj_value=raw_obj['value'],
                              atoms=raw_obj.get('atoms', {}),
                              flows=raw_obj.get('flows', {}),
                              help=raw_obj['help']
                              )

    def get_obj_flow_definition(self, obj_name, flow_name):
        obj_def = self.get_obj_definition(obj_name)
        raw_flow = obj_def.flows[flow_name]
        return maps.NamedDict(atoms=raw_flow['atoms'],
                              help=raw_flow['help'],
                              enabled=raw_flow['enabled'],
                              inputs=raw_flow['inputs'],
                              pre_run=raw_flow.get('pre_run', []),
                              post_run=raw_flow.get('post_run', []),
                              type=raw_flow['type'],
                              uuid=raw_flow['uuid'])

    def get_atom_definition(self, obj_name, atom_name):
        obj_def = self.get_obj_definition(obj_name)
        raw_atom = obj_def.atoms[atom_name]
        return maps.NamedDict(help=raw_atom['help'],
                              enabled=raw_atom['enabled'],
                              inputs=raw_atom.get('inputs').get('mandatory'),
                              outputs=raw_atom.get('outputs', []),
                              uuid=raw_atom['uuid'])

    def get_flow_definition(self, flow_name):
        raw_ns = "namespace.%s" % self.ns_name

        if hasattr(NS, "compiled_definitions"):
            raw_flow = NS.compiled_definitions.get_parsed_defs()[
                raw_ns][
                'flows'][flow_name]
        else:
            raw_flow = self.current_ns.definitions.get_parsed_defs()[raw_ns][
                'flows'][flow_name]
        return maps.NamedDict(atoms=raw_flow['atoms'],
                              help=raw_flow['help'],
                              enabled=raw_flow['enabled'],
                              inputs=raw_flow['inputs'],
                              pre_run=raw_flow.get('pre_run', []),
                              post_run=raw_flow.get('post_run', []),
                              type=raw_flow['type'],
                              uuid=raw_flow['uuid'])

    def _register_subclasses_to_ns(self):
        # registers all subclasses of BaseObject, BaseFlow, BaseAtom to
        # NS
        LOG.info("Finding objects in namespace.%s.objects", self.ns_name)

        ns_root = importlib.import_module(self.ns_src).__path__[0]

        # register objects and atoms, flows inside the objects
        ns_objects_path = ns_root + "/objects"
        ns_objects_prefix = self.ns_src + ".objects."
        objs = self._list_modules_in_package_path(ns_objects_path,
                                                  ns_objects_prefix)
        for name, obj_fqdn in objs:
            obj = importlib.import_module(obj_fqdn)
            for obj_cls in inspect.getmembers(obj, inspect.isclass):
                if issubclass(obj_cls[1], objects.BaseObject):
                    obj_name = obj_cls[0]
                    LOG.info("Registering object namespace.%s.objects.%s",
                             self.ns_name, obj_name)
                    self._add_object(obj_name, obj_cls[1])

                    ns_object_atoms_path = obj.__path__[0] + "/atoms"
                    ns_object_atoms_prefix = obj_fqdn + ".atoms."
                    LOG.info("Finding atoms in "
                             "namespace.%s.objects.%s.atoms", self.ns_name,
                             obj_name)
                    for atom_name, atom_fqdn in \
                        self._list_modules_in_package_path(
                            ns_object_atoms_path,
                            ns_object_atoms_prefix):
                        atom = importlib.import_module(atom_fqdn)

                        for atom_cls in inspect.getmembers(atom,
                                                           inspect.isclass):
                            if issubclass(atom_cls[1], BaseAtom):
                                LOG.info("Registering atom "
                                         "namespace.%s.objects.%s.atoms.%s",
                                         self.ns_name, obj_name,
                                         atom_cls[1].__name__)

                                self._add_atom(obj_name,
                                               atom_cls[1].__name__,
                                               atom_cls[1])

                    ns_object_flows_path = obj.__path__[0] + "/flows"
                    ns_object_flows_prefix = obj_fqdn + ".flows."
                    LOG.info("Finding flows in "
                             "namespace.%s.objects.%s.flows", self.ns_name,
                             obj_name)
                    for flow_name, flow_fqdn in \
                        self._list_modules_in_package_path(
                            ns_object_flows_path,
                            ns_object_flows_prefix):
                        flow = importlib.import_module(flow_fqdn)

                        for flow_cls in inspect.getmembers(flow,
                                                           inspect.isclass):
                            if issubclass(flow_cls[1], flows.BaseFlow):
                                LOG.info("Registering flow "
                                         "namespace.%s.objects.%s.flow.%s",
                                         self.ns_name, obj_name,
                                         flow_cls[1].__name__)
                                self._add_obj_flow(obj_name,
                                                   flow_cls[1].__name__,
                                                   flow_cls[1])

        ns_flows_path = ns_root + "/flows"
        ns_flows_prefix = self.ns_src + ".flows."
        flowz = self._list_modules_in_package_path(ns_flows_path,
                                                   ns_flows_prefix)
        LOG.info("Finding flows in namespace.%s.flows", self.ns_name)
        for name, flow_fqdn in flowz:
            the_flow = importlib.import_module(flow_fqdn)
            for flow_cls in inspect.getmembers(the_flow, inspect.isclass):
                if issubclass(flow_cls[1], flows.BaseFlow):
                    LOG.info("Registering flow namespace.%s.flows.%s",
                             self.ns_name, flow_cls[0])
                    self._add_flow(flow_cls[0], flow_cls[1])

    def _list_modules_in_package_path(self, package_path, prefix):
        modules = []
        for importer, name, ispkg in pkgutil.walk_packages(
                path=[package_path]):
            modules.append((name, prefix + name))
        return modules
