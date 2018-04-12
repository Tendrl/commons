import json
import os
import socket
import sys
import uuid

import etcd

from tendrl.commons import objects
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import event_utils
from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils import time_utils


NODE_ID = None


class NodeContext(objects.BaseObject):

    def __init__(self, node_id=None, fqdn=None, ipv4_addr=None,
                 tags=None, status=None, sync_status=None,
                 last_sync=None, updated_at=None, pkey=None,
                 *args, **kwargs):
        super(NodeContext, self).__init__(*args, **kwargs)
        self.node_id = node_id or self._get_node_id() or self._create_node_id()
        self.fqdn = fqdn
        self.ipv4_addr = ipv4_addr
        if self.fqdn:
            self.ipv4_addr = socket.gethostbyname(self.fqdn)

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
        self.pkey = pkey or self.fqdn
        self.value = 'nodes/{0}/NodeContext'

    def _create_node_id(self):
        node_id = str(uuid.uuid4())
        try:
            logger.log(
                "debug",
                NS.publisher_id,
                {"message": "Registered Node (%s) with " % node_id}
            )
        except KeyError:
            sys.stdout.write("message: Registered Node (%s) \n" % node_id)

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
            self._ttl = ttl
            etcd_utils.refresh(status, ttl)

    def on_change(self, attr, prev_value, current_value):
        if attr == "status":
            if current_value is None:
                self.status = "DOWN"
                self.save()
                msg = "Node {0} is DOWN".format(self.fqdn)
                event_utils.emit_event(
                    "node_status",
                    self.status,
                    msg,
                    "node_{0}".format(self.fqdn),
                    "WARNING",
                    node_id=self.node_id
                )

                _tc = NS.tendrl.objects.TendrlContext(
                    node_id=self.node_id
                ).load()
                _tag = "provisioner/%s" % _tc.integration_id
                if _tag in self.tags:
                    _index_key = "/indexes/tags/%s" % _tag
                    self.tags.remove(_tag)
                    self.save()
                    etcd_utils.delete(_index_key)
                    _msg = "node_sync, STALE provisioner node "\
                        "found! re-configuring monitoring "\
                        "(job-id: %s) on this node"
                    payload = {
                        "tags": ["tendrl/node_%s" % self.node_id],
                        "run": "tendrl.flows.ConfigureMonitoring",
                        "status": "new",
                        "parameters": {
                            'TendrlContext.integration_id': _tc.integration_id
                        },
                        "type": "node"
                    }
                    _job_id = str(uuid.uuid4())
                    NS.tendrl.objects.Job(
                        job_id=_job_id,
                        status="new",
                        payload=payload
                    ).save()
                    logger.log(
                        "debug",
                        NS.publisher_id,
                        {"message": _msg % _job_id}
                    )

                if _tc.sds_name == "gluster":
                    bricks = etcd_utils.read(
                        "clusters/{0}/Bricks/all/{1}".format(
                            _tc.integration_id,
                            self.fqdn
                        )
                    )

                    for brick in bricks.leaves:
                        try:
                            etcd_utils.write(
                                "{0}/status".format(brick.key),
                                "Stopped"
                            )
                        except (etcd.EtcdAlreadyExist, etcd.EtcdKeyNotFound):
                            pass
