import json
import os
import socket
import sys
import uuid

import etcd


from tendrl.commons.event import Event
from tendrl.commons.message import Message

from tendrl.commons import objects
import traceback


MACHINE_ID = None
NODE_ID = None


class NodeContext(objects.BaseObject):

    def __init__(self, machine_id=None, node_id=None, fqdn=None,
                 tags=None, status=None, *args, **kwargs):
        super(NodeContext, self).__init__(*args, **kwargs)
        self.machine_id = machine_id or self._get_machine_id()
        self.node_id = node_id or self._get_node_id() or self._create_node_id()
        self.fqdn = fqdn or socket.getfqdn()

        curr_tags = []
        try:
            curr_tags = NS._int.client.read("/nodes/%s/NodeContext/tags" % self.node_id).value
        except etcd.EtcdKeyNotFound:
            pass
        
        try:
            curr_tags = json.loads(curr_tags)
        except (ValueError, TypeError):
            # No existing tags
            pass
        self.tags = tags or []
        self.tags += NS.config.data['tags']
        self.tags += curr_tags
        self.tags = list(set(self.tags))
        
        self.status = status or "UP"
        self.value = 'nodes/{0}/NodeContext'

    def _get_machine_id(self):
        if MACHINE_ID:
            return MACHINE_ID
        
        out = None
        try:
            with open('/etc/machine-id') as f:
                out = f.read().strip('\n')
                global MACHINE_ID
                MACHINE_ID = out
        except IOError as ex:
            exc_type, exc_value, exc_tb = sys.exc_info()
            traceback.print_exception(
                exc_type, exc_value, exc_tb, file=sys.stderr)
            sys.stderr.write(
                "Unable to find machine id.%s\n" % str(ex))  
        return out

    def _create_node_id(self):
        node_id = str(uuid.uuid4())
        index_key = "/indexes/machine_id/%s" % self.machine_id
        NS._int.wclient.write(index_key, node_id, prevExist=False)
        try:
            Event(
                Message(
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={"message": "Registered Node (%s) with machine_id==%s" % (node_id, self.machine_id)
                         }
            )
        )
        except KeyError:
            sys.stdout.write("message: Registered Node (%s) with machine_id==%s" % (node_id, self.machine_id))
        local_node_id = "/var/lib/tendrl/node_id"
        if not os.path.exists(os.path.dirname(local_node_id)):
            os.makedirs(os.path.dirname(local_node_id))
        with open(local_node_id, 'wb+') as f:
            f.write(node_id)
        global NODE_ID
        NODE_ID = node_id
        return node_id

    def _get_node_id(self):
        if NODE_ID:
            return NODE_ID
        try:
            last_node_id =  NS._int.client.read("/indexes/machine_id/%s" % self.machine_id).value
            try:
                local_node_id = "/var/lib/tendrl/node_id"
                if os.path.isfile(local_node_id):
                    with open(local_node_id) as f:
                        node_id = f.read()
                        if node_id is None or node_id != last_node_id:
                            raise Exception("Cannot run tendrl-node-agent, machine-id (%s) in use by another node managed by Tendrl, please re-generate /etc/machine-id" % self.machine_id)
                        if node_id == last_node_id:
                            return last_node_id
            except (AttributeError, IOError):
                return None

        except etcd.EtcdKeyNotFound:
            try:
                Event(
                    Message(
                        priority="info",
                        publisher=NS.publisher_id,
                        payload={"message": "Unregistered Node found with machine_id==%s" % self.machine_id
                                }
                 )
                )
            except KeyError:
                sys.stdout.write("Unregistered Node found with machine_id==%s" %
                                 self.machine_id)

            return None

    def render(self):
        self.value = self.value.format(NS.node_context.node_id)
        return super(NodeContext, self).render()
