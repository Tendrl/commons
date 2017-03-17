# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     (1) Redistributions of source code must retain the above copyright
#     notice, this list of conditions and the following disclaimer.
#
#     (2) Redistributions in binary form must reproduce the above copyright
#     notice, this list of conditions and the following disclaimer in
#     the documentation and/or other materials provided with the
#     distribution.
#
#     (3)The name of the author may not be used to
#     endorse or promote products derived from this software without
#     specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
# IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
"""
A simplistic etcd orm.
"""

import json
import logging

from tendrl.commons.etcdobj import fields

LOG = logging.getLogger(__name__)


class _Server(object):
    """Parent class for all Server implementations.

    """

    def __init__(self, client):
        """Creates a new instance of a Server implementation.

        :param client: The etcd client to use.
        :type client: object
        :raises: ValueError
        """
        self.client = None
        self._verify_client(client)

    def _verify_client(self, client):
        """Does basic validation that the client can be used.

        :param client: The client to check.
        :type client: object
        :raises: ValueError
        """
        missing = []
        for method in ('write', 'read', 'delete'):
            if not callable(getattr(client, method, None)):
                missing.append(method)

        if missing:
            raise ValueError('The following methods are missing from the '
                             'client: {0}'.format(', '.join(missing)))

        self.client = client

    def save(self, obj):
        """Save an object.

        :param obj: An instance that subclasses EtcdObj
        :type obj: EtcdObj
        :returns: The same instance
        :rtype: EtcdObj
        """
        for item in obj.render():
            LOG.debug("Writing %s to %s", item['key'], item['value'])
            self.client.write(item['key'], item['value'], quorum=True)
        return obj

    def read(self, obj):
        """Retrieve an object.

        :param obj: An instance that subclasses EtcdObj
        :type obj: EtcdObj
        :returns: A filled out instance
        :rtype: EtcdObj
        """
        for item in obj.render():
            LOG.debug("Reading %s", item['key'])
            etcd_resp = self.client.read(item['key'], quorum=True)
            value = etcd_resp.value

            if item['dir']:
                key = item['key'].split('/')[-1]
                dct = getattr(obj, item['name'])
                dct[key] = value
            else:
                setattr(obj, item['name'], value)
        return obj


class Server(_Server):
    """Server implementation which creates an etcd.Client instance as its

    client.

    """

    def __init__(self, etcd_kwargs):
        """Creates a new instance of Server.

        :param etcd_kwargs: The keyword arguments used to create an etcd.Client
        :type etcd_kwargs: dict
        :raises: ValueError
        """
        import etcd
        if not etcd_kwargs:
            etcd_kwargs = dict()
        etcd_kwargs["allow_reconnect"] = True
        etcd_kwargs["per_host_pool_size"] = 20
        super(Server, self).__init__(
            etcd.Client(**etcd_kwargs))


class EtcdObj(object):
    """Class all objects which want to persist to etcd must subclass.

    """

    def __init__(self, **kwargs):  # pragma: no cover
        """Initializes a new instance. Required for __new__.

        :param kwargs: All keyword arguments.
        :type kwargs: dict
        """
        super(EtcdObj, self).__init__()
        self._fields = []
        for key in dir(self):
            if not key.startswith('_'):
                attr = getattr(self, key)
                if issubclass(attr.__class__, fields.Field):
                    self._fields.append(key)
                    if key in kwargs.keys():
                        attr.value = kwargs[key]

    def __setattr__(self, name, value):
        """Overridden setattr to catch fields or pass along if not a field.

        :param name: The name of the field.
        :type name: str
        :param value: The value to set on name.
        :type value: any
        """
        if name == "_fields":
            object.__setattr__(self, name, value)
            return
        attr = object.__getattribute__(self, name)
        if name in self._fields:
            attr.value = value
        else:
            object.__setattr__(self, name, value)

    def __getattribute__(self, name):
        """Overridden  getattribute to catch fields or pass along if not a

        field.

        :param name: The name of the field.
        :type name: str
        :returns: The value of the field or attribute
        :rtype: any
        :raises: AttributeError
        """
        if name == "_fields":
            return object.__getattribute__(self, name)
        if name in object.__getattribute__(self, '_fields'):
            return object.__getattribute__(self, name).value
        else:
            return object.__getattribute__(self, name)

    def render(self):
        """Renders the instance into a structure for settings in etcd.

        :returns: The structure to use for setting.
        :rtype: list(dict{key=str,value=any})
        """
        rendered = []
        for x in self._fields:
            items = object.__getattribute__(self, x).render()
            if type(items) != list:
                items = [items]
            for i in items:
                i['key'] = '/{0}/{1}'.format(self.__name__, i['key'])
                rendered.append(i)
        return rendered

    @property
    def json(self):
        """Dumps the entire object as a json structure.

        """
        data = {}
        for field in self._fields:
            # FIXME: This is dumb :-)
            attribute = object.__getattribute__(self, field)
            data[attribute.name] = json.loads(attribute.json)
            # Flatten if needed
            if attribute.name in data[attribute.name].keys():
                data[attribute.name] = data[attribute.name][attribute.name]
        return json.dumps(data)

    def to_tendrl_obj(self):
        klass = self.__class__
        result = self._tendrl_cls()
        for key in dir(klass):
            if not key.startswith('_'):
                attr = getattr(klass, key)
                if issubclass(attr.__class__, fields.Field):
                    setattr(result, key, attr.value)
        return result
