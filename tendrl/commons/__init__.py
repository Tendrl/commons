__version__ = '1.2.1'

import namespaces as ns

from tendrl.commons import objects
from tendrl.commons import flows
from tendrl.commons.objects import atoms
from tendrl.commons import etcdobj
from tendrl.commons import log


class CommonNS(object):
    def __init__(self):
        super(CommonNS, self).__init__()
        import __builtin__
        setattr(__builtin__, "tendrl_ns", self)

        ns_str = self.to_str.split(".")[-1]
        # Create the component namespace
        setattr(self, ns_str,
                ns.Namespace(objects=ns.Namespace(), flows=ns.Namespace()))
        self.register_subclasses_to_ns()

        ns_obj = getattr(self, ns_str)
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
        return getattr(self, self.to_str.split(".")[-1])

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
        def _discover_subclasses(cls, _seen=None):
            if not isinstance(cls, type):
                raise TypeError('New-style class required' % cls)
            if _seen is None: _seen = set()
            try:
                subs = cls.__subclasses__()
            except TypeError:  # fails only when cls is type
                subs = cls.__subclasses__(cls)
            for sub in subs:
                if sub not in _seen:
                    _seen.add(sub)
                    yield sub
                    for sub in _discover_subclasses(sub, _seen):
                        yield sub
        for base_class in [objects.BaseObject, flows.BaseFlow, atoms.BaseAtom]:
            for sub_class in _discover_subclasses(base_class):
                base_name = base_class.__name__
                sub_name = sub_class.__name__
                if "Object" in base_name:
                    self.add_object(sub_name, sub_class)
                if "Atom" in base_name:
                    self.add_atom(sub_class.obj.__name__, sub_name, sub_class)
                if "Flow" in base_name:
                    if hasattr(sub_class, "obj"):
                        self.add_obj_flow(sub_class.obj.__name__, sub_name,
                                          sub_class)
                    else:
                        self.add_flow(sub_name, sub_class)
