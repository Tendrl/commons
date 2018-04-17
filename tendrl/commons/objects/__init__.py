import etcd

import abc
import copy
import hashlib
import json
import six
import sys
import threading

from tendrl.commons.event import Event
from tendrl.commons.message import ExceptionMessage
from tendrl.commons.utils.central_store import utils as cs_utils
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils import time_utils


def thread_safe(thread_unsafe_method):
    def thread_safe_method(self, *args, **kws):
        with self._lock:
            return thread_unsafe_method(self, *args, **kws)

    return thread_safe_method


@six.add_metaclass(abc.ABCMeta)
class BaseObject(object):
    def __init__(self, *args, **kwargs):
        self._ttl = None
        self._lock = threading.RLock()
        self.hash = None
        self._rendered = None
        # Tendrl internal objects should populate their own self._defs
        if not hasattr(self, "internal"):
            self._defs = BaseObject.load_definition(self)
        if hasattr(self, "internal"):
            if not hasattr(self, "_defs"):
                raise Exception("Internal Object must provide its own "
                                "definition via '_defs' attr")

    def load_definition(self):
        try:
            logger.log(
                "debug",
                NS.publisher_id,
                {"message": "Load definitions (.yml) for "
                            "namespace.%s.objects.%s" %
                            (self._ns.ns_name,
                             self.__class__.__name__)}
            )
        except KeyError:
            sys.stdout.write(
                "Load definitions (.yml) for namespace.%s.objects"
                ".%s \n" % (self._ns.ns_name, self.__class__.__name__)
            )
        try:
            return self._ns.get_obj_definition(self.__class__.__name__)
        except KeyError as ex:
            msg = "Could not find definitions (.yml) for " \
                  "namespace.%s.objects.%s" %\
                  (self._ns.ns_name, self.__class__.__name__)
            try:
                Event(
                    ExceptionMessage(
                        priority="debug",
                        publisher=NS.publisher_id,
                        payload={"message": "error",
                                 "exception": ex}
                    )
                )
            except KeyError:
                sys.stdout.write(str(ex) + "\n")
            try:
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {"message": msg}
                )
            except KeyError:
                sys.stdout.write(msg + "\n")
            raise Exception(msg)

    @thread_safe
    def save(self, update=True, ttl=None):
        rendered_obj = self.render()
        if "Message" not in self.__class__.__name__:
            # If local object.hash is equal to
            # central_store object.hash, return
            if self.hash_compare_with_central_store(ttl=ttl):
                return
        watchables = self._defs.get("watch_attrs", [])
        if self.__class__.__name__ in ['Config', 'Definition'] or \
            len(watchables) > 0:
            for item in rendered_obj:
                if item['name'] in watchables:
                    _type = self._defs.get("attrs", {}).get(
                        item['name'],
                        {}
                    ).get("type")
                    if _type and _type.lower() in ['json', 'list'] and \
                        item['value']:
                        try:
                            item['value'] = json.dumps(item['value'])
                        except ValueError:
                            _msg = "Error save() attr %s for object %s" % \
                                   (item['name'], self.__name__)
                            logger.log(
                                "debug",
                                NS.publisher_id,
                                {"message": _msg}
                            )
                    etcd_utils.write(item['key'], item['value'], quorum=True)

        data_key = self.value + '/data'
        etcd_utils.write(data_key, self.json)
        updated_at_key = self.value + '/updated_at'
        hash_key = self.value + '/hash'
        etcd_utils.write(updated_at_key, str(time_utils.now()))
        if hasattr(self, 'hash'):
            etcd_utils.write(hash_key, self.hash)

        if ttl:
            etcd_utils.refresh(self.value, ttl)

        self.watch_attrs()

    @thread_safe
    def load_all(self):
        self.render()
        value = '/'.join(self.value.split('/')[:-1])
        etcd_resp = etcd_utils.read(value)

        ins = []
        for item in etcd_resp.leaves:
            # When directory is not empty then NS._int.client.read(key)
            # will return key + directory id as new key. If directory is
            # empty then it will return key only. When directory is
            # not present then it will raise EtcdKeyNotFound
            if item.key.strip("/") != value.strip("/"):
                # if dir is empty then item.key and value is same
                self.value = item.key
                ins.append(self.load())
        return ins

    @thread_safe
    def load(self):
        self.render()
        if "Message" not in self.__class__.__name__:
            # If local object.hash is equal to
            # central_store object.hash, return
            if self.hash_compare_with_central_store():
                return self

        key = self.value + '/data'
        try:
            val_str = etcd_utils.read(key).value
        except etcd.EtcdKeyNotFound:
            return self
        loc_dict = json.loads(val_str)
        for attr_name, attr_val in vars(self).iteritems():
            if not attr_name.startswith('_') and \
                attr_name not in ["value", "list"]:
                _type = self._defs.get("attrs", {}).get(
                    attr_name,
                    {}
                ).get("type")
                if loc_dict.get(attr_name) in [None, ""]:
                    if _type and _type.lower() == 'list':
                        setattr(self, attr_name, list())
                    if _type and _type.lower() == 'json':
                        setattr(self, attr_name, dict())
                else:
                    if _type and _type.lower() in ['list']:
                        setattr(
                            self,
                            attr_name,
                            json.loads(loc_dict[attr_name])
                        )
                    else:
                        setattr(self, attr_name, loc_dict[attr_name])
        return self

    @thread_safe
    def exists(self):
        self.render()
        _exists = True
        try:
            etcd_utils.read("/{0}".format(self.value))
        except etcd.EtcdKeyNotFound as ex:
            _exists = False
        return _exists

    @thread_safe
    def _map_vars_to_tendrl_fields(self):
        _fields = {}
        for attr, value in vars(self).iteritems():
            _type = self._defs.get("attrs", {}).get(attr,
                                                    {}).get("type")
            if _type:
                _type = _type.lower()

            if value is None:
                value = ""
            if attr.startswith("_") or attr in ['value', 'list']:
                continue
            _fields[attr] = cs_utils.to_tendrl_field(attr, value, _type)

        return _fields

    @thread_safe
    def render(self):
        """Renders the instance into a structure for central store based on

        its key (self.value)

        :returns: The structure to use for setting.
        :rtype: list(dict{key=str,value=any})
        """
        old_hash = self.hash
        if old_hash == self._hash():
            return self._rendered
        rendered = []
        _fields = self._map_vars_to_tendrl_fields()
        if _fields:
            for name, field in _fields.iteritems():
                items = field.render()
                if type(items) != list:
                    items = [items]
                for i in items:
                    i['key'] = '/{0}/{1}'.format(self.value, i['key'])
                    rendered.append(i)
        self._rendered = rendered
        return self._rendered

    @property
    @thread_safe
    def json(self):
        """Dumps the entire object as a json structure.

        """
        data = {}
        _fields = self._map_vars_to_tendrl_fields()
        if _fields:
            for name, field in _fields.iteritems():
                if field.name == "hash":
                    continue
                data[field.name] = json.loads(field.json)
                # Flatten if needed
                if field.name in data[field.name].keys():
                    data[field.name] = data[field.name][field.name]

        return json.dumps(data)

    @thread_safe
    def _hash(self):
        self.updated_at = None

        # Above items cant be part of hash
        _obj_str = "".join(sorted(self.json))
        self.hash = hashlib.md5(_obj_str).hexdigest()
        return self.hash

    @thread_safe
    def hash_compare_with_central_store(self, ttl=None):
        try:
            # Generate current in memory object hash
            self.hash = self._hash()
            _hash_key = "/{0}/hash".format(self.value)
            _stored_hash = None
            try:
                _stored_hash = etcd_utils.read(_hash_key).value
            except etcd.EtcdKeyNotFound:
                return False
            if self.hash == _stored_hash:
                # No changes in stored object and current object,
                # dont save current object to central store
                if ttl:
                    etcd_utils.refresh(self.value, ttl)
                return True
            else:
                return False
        except TypeError:
            # no hash for this object, save the current hash as is
            return False

    @thread_safe
    def invalidate_hash(self):
        self.render()
        _hash_key = "/{0}/hash".format(self.value)
        etcd_utils.delete(_hash_key)

    @thread_safe
    def _copy_vars(self):
        # Creates a copy intance of $obj using it public vars
        _public_vars = {}
        for attr, value in vars(self).iteritems():
            if attr.startswith("_") or attr in ['hash', 'updated_at',
                                                'value', 'list']:
                continue
            if type(value) in [dict, list]:
                value = copy.deepcopy(value)
            _public_vars[attr] = value
        return self.__class__(**_public_vars)

    @thread_safe
    def watch_attrs(self):
        if self.value:
            watchables = self._defs.get("watch_attrs", [])
            for attr in watchables:
                key = "{0}/{1}".format(self.value.rstrip("/"), attr)
                if key not in NS._int.watchers:
                    watcher = threading.Thread(target=cs_utils.watch,
                                               args=(copy.copy(self),
                                                     key))
                    watcher.setDaemon(True)
                    NS._int.watchers[key] = watcher
                    watcher.start()


@six.add_metaclass(abc.ABCMeta)
class BaseAtom(object):
    def __init__(self, parameters=None):
        self.parameters = parameters or dict()

        # Tendrl internal atoms should populate their own self._defs
        if not hasattr(self, "internal"):
            self._defs = BaseAtom.load_definition(self)
        if hasattr(self, "internal"):
            if not hasattr(self, "_defs"):
                raise Exception("Internal Atom must provide its own "
                                "definition via '_defs' attr")

    def load_definition(self):
        try:
            logger.log(
                "debug",
                NS.publisher_id,
                {"message": "Load definitions (.yml) for "
                            "namespace.%s."
                            "objects.%s.atoms.%s" %
                            (self._ns.ns_name, self.obj.__name__,
                             self.__class__.__name__)}
            )
        except KeyError:
            sys.stdout.write(
                "Load definitions (.yml) for "
                "namespace.%s.objects.%s."
                "atoms.%s \n" %
                (self._ns.ns_name, self.obj.__name__,
                 self.__class__.__name__)
            )
        try:
            return self._ns.get_atom_definition(
                self.obj.__name__,
                self.__class__.__name__
            )
        except KeyError as ex:
            msg = "Could not find definitions (.yml) for" \
                  "namespace.%s.objects.%s.atoms.%s" % \
                  (
                      self._ns.ns_src,
                      self.obj.__name__,
                      self.__class__.__name__
                  )
            try:
                Event(
                    ExceptionMessage(
                        priority="debug",
                        publisher=NS.publisher_id,
                        payload={"message": "Error", "exception": ex}
                    )
                )
            except KeyError:
                sys.stderr.write("Error: %s \n" % ex)
            try:
                logger.log(
                    "debug",
                    NS.publisher_id,
                    {"message": msg}
                )
            except KeyError:
                sys.stderr.write(msg + "\n")
            raise Exception(msg)

    @abc.abstractmethod
    def run(self):
        raise AtomNotImplementedError(
            'define the function run to use this class'
        )


class AtomNotImplementedError(NotImplementedError):
    def __init__(self, err):
        self.message = "run function not implemented. {}".format(err)
        super(AtomNotImplementedError, self).__init__(self.message)


class AtomExecutionFailedError(Exception):
    def __init__(self, err):
        self.message = "Atom Execution failed. Error:" + \
                       " {}".format(err)
        super(AtomExecutionFailedError, self).__init__(self.message)
