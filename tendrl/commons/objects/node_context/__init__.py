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


NODE_ID = None


class NodeContext(objects.BaseObject):

    def __init__(self, node_id=None, fqdn=None, ipv4_addr=None,
                 tags=None, status=None, sync_status=None,
                 last_sync=None, pkey=None,
                 locked_by=None, *args, **kwargs):
        super(NodeContext, self).__init__(*args, **kwargs)
        self.node_id = node_id or self._get_node_id() or self._create_node_id()
        self.fqdn = fqdn
        self.ipv4_addr = ipv4_addr
        if self.fqdn:
            self.ipv4_addr = socket.gethostbyname(self.fqdn)
        self.locked_by = locked_by

        curr_tags = []
        try:
            _nc_data = etcd_utils.read(
                "/nodes/%s/NodeContext/data" % self.node_id
            ).value
            curr_tags = json.loads(_nc_data)['tags']
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
        if self.status == "UP" and ttl is None:
            # Set ttl always when node status in up
            ttl = int(
                NS.config.data.get("sync_interval", 60)
            )
        if ttl:
            self._ttl = ttl
            try:
                etcd_utils.refresh(status, ttl)
            except etcd.EtcdKeyNotFound:
                pass

    def on_change(self, attr, prev_value, current_value):
        if attr == "status" and "tendrl/monitor" in NS.node_context.tags:
            _tc = NS.tendrl.objects.TendrlContext(
                node_id=self.node_id
            ).load()
            # Check node is managed
            _cnc = NS.tendrl.objects.ClusterNodeContext(
                node_id=self.node_id,
                integration_id=_tc.integration_id
            ).load()
            if current_value is None and _tc.integration_id:
                self.status = "DOWN"
                self.save()
                if str(_cnc.is_managed).lower() == "yes":
                    msg = "Node {0} is DOWN".format(self.fqdn)
                    event_utils.emit_event(
                        "node_status",
                        self.status,
                        msg,
                        "node_{0}".format(self.fqdn),
                        "WARNING",
                        node_id=self.node_id,
                        integration_id=_tc.integration_id
                    )
                    # Load cluster_node_context will load node_context
                    # and it will be updated with latest values
                    _cnc_new = \
                        NS.tendrl.objects.ClusterNodeContext(
                            node_id=self.node_id,
                            integration_id=_tc.integration_id,
                            first_sync_done=_cnc.first_sync_done,
                            is_managed=_cnc.is_managed
                        )
                    _cnc_new.save()
                    del _cnc_new
                    # Update cluster details
                    self.update_cluster_details(_tc.integration_id)
                    _tag = "provisioner/%s" % _tc.integration_id
                    if _tag in self.tags:
                        _index_key = "/indexes/tags/%s" % _tag
                        self.tags.remove(_tag)
                        self.save()
                        try:
                            etcd_utils.delete(_index_key)
                        except etcd.EtcdKeyNotFound:
                            pass
                    if _tc.sds_name in ["gluster", "RHGS"]:
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
                            except (
                                etcd.EtcdAlreadyExist,
                                etcd.EtcdKeyNotFound
                            ):
                                pass
            elif current_value == "UP" and str(
                    _cnc.is_managed).lower() == "yes":
                msg = "{0} is UP".format(self.fqdn)
                event_utils.emit_event(
                    "node_status",
                    "UP",
                    msg,
                    "node_{0}".format(self.fqdn),
                    "INFO",
                    node_id=self.node_id,
                    integration_id=_tc.integration_id
                )
            del _cnc

    def update_cluster_details(self, integration_id):
        try:
            nodes = etcd_utils.read(
                "/clusters/%s/nodes" % integration_id
            )
            for node in nodes.leaves:
                _cnc = NS.tendrl.objects.ClusterNodeContext(
                    node_id=node.key.split("/")[-1],
                    integration_id=integration_id
                ).load()
                # Verify all nodes in a cluster are down
                if str(_cnc.status).lower() != "down" and \
                        str(_cnc.is_managed).lower() == "yes":
                    # Any one managed node not down don't update
                    # cluster details, No need to consider unmanaged
                    # nodes
                    return
            # when all managed nodes are down update cluster details
            global_details = NS.tendrl.objects.GlobalDetails(
                integration_id=integration_id
            ).load()
            # Update cluster as unhealthy
            if global_details.status.lower() == "healthy":
                global_details.status = "unhealthy"
                global_details.save()
                _cluster = NS.tendrl.objects.Cluster(
                    integration_id=integration_id
                ).load()
                msg = "Cluster:%s is %s" % (
                    _cluster.short_name, "unhealthy")
                instance = "cluster_%s" % integration_id
                event_utils.emit_event(
                    "cluster_health_status",
                    "unhealthy",
                    msg,
                    instance,
                    'WARNING',
                    integration_id=integration_id
                )
            # Update all bricks are down
            nodes = etcd_utils.read(
                "/clusters/%s/Bricks/all" % integration_id
            )
            for node in nodes.leaves:
                bricks = NS.tendrl.objects.GlusterBrick(
                    integration_id,
                    fqdn=node.key.split("/")[-1]
                ).load_all()
                for brick in bricks:
                    if brick.status.lower() != "stopped":
                        brick.status = "Stopped"
                        brick.save()
                        msg = ("Brick:%s in volume:%s has %s") % (
                            brick.brick_path,
                            brick.vol_name,
                            "Stopped"
                        )
                        instance = "volume_%s|brick_%s" % (
                            brick.vol_name,
                            brick.brick_path
                        )
                        event_utils.emit_event(
                            "brick_status",
                            "Stopped",
                            msg,
                            instance,
                            "WARNING",
                            integration_id=integration_id,
                            tags={"entity_type": "brick",
                                  "volume_name": brick.vol_name,
                                  "node_id": brick.node_id
                                  }
                        )
            # Update all volumes are down
            volumes = NS.tendrl.objects.GlusterVolume(
                integration_id
            ).load_all()
            for volume in volumes:
                if volume.state.lower() != "down":
                    volume.state = "down"
                    volume.status = "Stopped"
                    volume.save()
                    msg = "Volume:%s is %s" % (volume.name, "down")
                    instance = "volume_%s" % volume.name
                    event_utils.emit_event(
                        "volume_state",
                        "down",
                        msg,
                        instance,
                        "WARNING",
                        integration_id=integration_id,
                        tags={"entity_type": "volume",
                              "volume_name": volume.name
                              }
                    )
        except etcd.EtcdKeyNotFound:
            pass
