import abc
import etcd
import six
import sys

from tendrl.commons.central_store import utils as cs_utils
from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage, Message

@six.add_metaclass(abc.ABCMeta)
class BaseObject(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "internal"):
            if hasattr(cls, "load_definition"):
                raise Exception("Non internal Object cannot use load_definition, must have definition in (.yml)")
        return object.__new__(cls, *args, **kwargs)

    def __init__(self):
        # Tendrl internal objects should populate their own self._defs
        if not hasattr(self, "internal"):
            self._defs = self.load_definition()
        if hasattr(self, "internal"):
            if not hasattr(self, "_defs"):
                raise Exception("Internal Object must provide its own definition via '_defs' attr")

    def __new__(cls, *args, **kwargs):

        super_new = super(BaseObject, cls).__new__
        if super_new is object.__new__:
            instance = super_new(cls)
        else:
            instance = super_new(cls, *args, **kwargs)

        return instance

    def load_definition(self):
        try:
            Event(
                Message(
                    priority="debug",
                    publisher=NS.publisher_id,
                    payload={"message": "Load definitions for namespace.%s."
                                        "objects.%s" % (self._ns.ns_name,
                                                        self.__class__.__name__)
                             }
                )
            )
        except KeyError:
            sys.stdout.write("Load definitions for namespace.%s.objects.%s" %
                             (self._ns.ns_name, self.__class__.__name__))
        try:
            return self._ns.get_obj_definition(self.__class__.__name__)
        except KeyError as ex:
            msg = "Could not find definitions for namespace.%s.objects.%s" %\
                  (self._ns.ns_name, self.__class__.__name__)
            try:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "error",
                                 "exception": ex}
                    )
                )
            except KeyError:
                sys.stdout.write(str(ex))
            try:
                Event(
                    Message(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": msg}
                    )
                )
            except KeyError:
                sys.stdout.write(msg)
            raise Exception(msg)

    def save(self):
        try:
            current_obj = self.load()
            for attr, val in self.__dict__.iteritems():
                if attr in ["defs"]:
                    continue
                if val is None:
                    continue
                if attr.startswith("_"):
                    continue

                setattr(current_obj, attr, val)

            cls_etcd = cs_utils.to_etcdobj(self._etcd_cls, current_obj)
        except etcd.EtcdKeyNotFound as ex:
            # No need to log the error. This would keep happening
            # till first cluster is imported/created or some data
            # synchronized in central store.
            # This un-necessarily hog the log as every few seconds
            # these errors would be logged.
            cls_etcd = cs_utils.to_etcdobj(self._etcd_cls, self)

        getattr(NS.central_store_thread, "save_%s" %
                self.__class__.__name__.lower())(cls_etcd())

    def load(self):
        cls_etcd = cs_utils.to_etcdobj(self._etcd_cls, self)
        result = NS.etcd_orm.read(cls_etcd())
        return result.to_tendrl_obj()


@six.add_metaclass(abc.ABCMeta)
class BaseAtom(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, "internal"):
            if hasattr(cls, "load_definition"):
                raise Exception("Non internal Atom cannot use load_definition, must have definition in (.yml)")
        return object.__new__(cls, *args, **kwargs)

    def __init__(self, parameters=None):
        self.parameters = parameters

        # Tendrl internal atoms should populate their own self._defs
        if not hasattr(self, "internal"):
            self._defs = self.load_definition()
        if hasattr(self, "internal"):
            if not hasattr(self, "_defs"):
                raise Exception("Internal Atom must provide its own definition via '_defs' attr")

    def load_definition(self):
        try:
            Event(
                Message(
                    priority="debug",
                    publisher=NS.publisher_id,
                    payload={"message": "Load definitions for namespace.%s."
                                        "objects.%s.atoms.%s" %
                                        (self._ns.ns_name, self.obj.__name__,
                                         self.__class__.__name__)
                             }
                )
            )
        except KeyError:
            sys.stdout.write("Load definitions for namespace.%s.objects.%s."
                             "atoms.%s" % (self._ns.ns_name, self.obj.__name__,
                                           self.__class__.__name__))
        try:
            return self._ns.get_atom_definition(self.obj.__name__,
                                                self.__class__.__name__)
        except KeyError as ex:
            msg = "Could not find definitions for" \
                  "namespace.%s.objects.%s.atoms.%s" % (self._ns.ns_src,
                                                        self.obj.__name__,
                                                        self.__class__.__name__
                                                        )
            try:
                Event(
                    ExceptionMessage(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": "Error", "exception": ex}
                    )
                )
            except KeyError:
                sys.stdout.write("Error: %s" % ex)
            try:
                Event(
                    Message(
                        priority="error",
                        publisher=NS.publisher_id,
                        payload={"message": msg}
                    )
                )
            except KeyError:
                sys.stdout.write(msg)
            raise Exception(msg)

    @abc.abstractmethod
    def run(self):
        raise AtomNotImplementedError(
            'define the function run to use this class'
        )

    def __new__(cls, *args, **kwargs):

        super_new = super(BaseAtom, cls).__new__
        if super_new is object.__new__:
            instance = super_new(cls)
        else:
            instance = super_new(cls, *args, **kwargs)

        return instance


class AtomNotImplementedError(NotImplementedError):
    def __init___(self, err):
        self.message = "run function not implemented. %s".format(err)


class AtomExecutionFailedError(Exception):
    def __init___(self, err):
        self.message = "Atom Execution failed. Error:" + \
                       " %s".format(err)
