import os
import socket
import sys
import uuid

import errno

from tendrl.commons.etcdobj import EtcdObj
from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.utils import cmd_utils

from tendrl.commons import objects
import traceback

class NodeContext(objects.BaseObject):

    def __init__(self, machine_id=None, node_id=None, fqdn=None,
                 tags=None, status=None, *args, **kwargs):
        super(NodeContext, self).__init__(*args, **kwargs)

        self.value = 'nodes/%s/NodeContext'
        self.machine_id = machine_id or self._get_machine_id()
        self.node_id = node_id or self._get_node_id() or self._create_node_id()
        self.fqdn = fqdn or socket.getfqdn()
        self.tags = tags or NS.config.data['tags']
        self.status = status or "UP"
        self._etcd_cls = _NodeContextEtcd

    def _get_machine_id(self):
        try:
            out = None 
            with open('/etc/machine-id') as f:
                out = f.read().strip('\n') 
        except IOError as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
            sys.stderr.write(
                "Unable to find machine id.%s\n" % str(ex))  
        return out

    def _create_node_id(self, node_id=None):
        node_id = node_id or str(uuid.uuid4())
        local_node_context = os.path.expandvars(
            "$HOME/.tendrl/node-agent/NodeContext")
        if not os.path.exists(os.path.dirname(local_node_context)):
            try:
                os.makedirs(os.path.dirname(local_node_context))
            except OSError as exc:
                if exc.errno != errno.EEXIST:
                    raise

        with open(local_node_context, 'wb+') as f:
            f.write(node_id)
            try:
                Event(
                    Message(
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={"message": "SET_LOCAL: NS.objects.NodeContext."
                                            "node_id==%s" % node_id
                                 }
                    )
                )
            except KeyError:
                sys.stdout.write("SET_LOCAL: NS.objects.NodeContext.node_id=="
                                 "%s" % node_id)
        return node_id

    def _get_node_id(self):
        try:
            local_node_context = \
                os.path.expandvars("$HOME/.tendrl/node-agent/NodeContext")
            if os.path.isfile(local_node_context):
                with open(local_node_context) as f:
                    node_id = f.read()
                    if node_id:
                        try:
                            Event(
                                Message(
                                    priority="info",
                                    publisher=NS.publisher_id,
                                    payload={"message": "GET_LOCAL: NS."
                                                        "objects.NodeContext."
                                                        "node_id==%s" % node_id
                                             }
                                )
                            )
                        except KeyError:
                            sys.stdout.write("GET_LOCAL: NS.objects."
                                             "NodeContext.node_id==%s" %
                                             node_id)
                        return node_id
        except AttributeError:
            return None


class _NodeContextEtcd(EtcdObj):
    """A table of the node context, lazily updated

    """
    __name__ = 'nodes/%s/NodeContext'
    _tendrl_cls = NodeContext

    def render(self):
        self.__name__ = self.__name__ % NS.node_context.node_id
        return super(_NodeContextEtcd, self).render()
