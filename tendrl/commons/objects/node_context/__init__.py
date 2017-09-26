import json
import os
import socket
import sys
import uuid

import etcd


from tendrl.commons.event import Event
from tendrl.commons.message import Message

from tendrl.commons import objects
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import time_utils


NODE_ID = None


class NodeContext(objects.BaseObject):

    def __init__(self, node_id=None, fqdn=None,
                 tags=None, status=None, sync_status=None, last_sync=None,
                 updated_at=None,
                 *args, **kwargs):
        super(NodeContext, self).__init__(*args, **kwargs)
        self.node_id = node_id or self._get_node_id() or self._create_node_id()
        self.fqdn = fqdn or socket.getfqdn()

        curr_tags = []
        try:
            curr_tags = NS._int.client.read("/nodes/%s/NodeContext/tags" %
                                            self.node_id).value
        except etcd.EtcdKeyNotFound:
            pass

        try:
            curr_tags = json.loads(curr_tags)
        except (ValueError, TypeError):
            # No existing tags
            pass
        self.tags = tags or []
        self.tags += NS.config.data.get('tags', [])
        self.tags += curr_tags
        self.tags = list(set(self.tags))

        self.status = status or "UP"
        self.sync_status = sync_status
        self.last_sync = last_sync
        self.updated_at = updated_at or str(time_utils.now())
        self.value = 'nodes/{0}/NodeContext'

    def _create_node_id(self):
        node_id = str(uuid.uuid4())
        try:
            Event(
                Message(
                    priority="debug",
                    publisher=NS.publisher_id,
                    payload={"message": "Registered Node (%s) with " % node_id
                             }
                )
            )
        except KeyError:
            sys.stdout.write("message: Registered Node (%s)" % node_id)

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

        local_node_id = "/var/lib/tendrl/node_id"
        if os.path.isfile(local_node_id):
            with open(local_node_id) as f:
                node_id = f.read()
                global NODE_ID
                NODE_ID = node_id
                return node_id

    def render(self):
        self.value = self.value.format(self.node_id or NS.node_context.node_id)
        return super(NodeContext, self).render()

    def save(self, update=True, ttl=None):
        super(NodeContext, self).save(update)
        status = self.value + "/status"
        if ttl:
            etcd_utils.refresh(status, ttl)
