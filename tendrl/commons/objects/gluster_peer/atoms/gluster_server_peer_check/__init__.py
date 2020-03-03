import etcd
import json
import socket

from tendrl.commons import objects
from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils import etcd_utils
from tendrl.commons.utils import log_utils as logger


class GlusterServerPeerError(Exception):
    pass


class GlusterServerPeerCheck(objects.BaseAtom):
    def __init__(self, *args, **kwargs):
        super(GlusterServerPeerCheck, self).__init__(*args, **kwargs)

    def run(self):
        gluster_server_peer_check = True
        try:
            integration_id = self.parameters['TendrlContext.integration_id']
            # get all detected node ids
            _node_ids_str = etcd_utils.read(
                "/indexes/tags/tendrl/integration/%s" % integration_id
            ).value
            _node_ids = json.loads(_node_ids_str)
            # exclude current node_id from the list
            _node_ids.remove(NS.node_context.node_id)
            # get gluster peer list
            cmd = cmd_utils.Command('gluster pool list')
            out, err, _ = cmd.run()
            gluster_fqdn = {}
            if not err:
                lines = out.split('\n')[1:]
                for line in lines:
                    if line != '':
                        peer = line.split()
                        peer_hostname = peer[-2]
                        if peer_hostname != "localhost":
                            fqdn = socket.gethostbyname(
                                peer_hostname
                            )
                            # if fqdn not found in detected node list then
                            # use this dict to print log message with actual
                            # peer hostnmae
                            gluster_fqdn[fqdn] = peer_hostname
            else:
                raise GlusterServerPeerError(err)
            # Always fqdn match will happen for gluster peer hostname/ip
            # with detected tendlr nodes hostname/ip
            for _node_id in _node_ids:
                node_obj = NS.tendrl.objects.NodeContext(
                    node_id=_node_id
                ).load()
                node_fqdn = socket.gethostbyname(
                    node_obj.fqdn
                )
                if node_fqdn in list(gluster_fqdn.keys()):
                    del gluster_fqdn[node_fqdn]
            # if any fqdn remaining then its means not all nodes are detected
            if len(list(gluster_fqdn.keys())) > 0:
                logger.log(
                    "error",
                    NS.publisher_id,
                    {"message": "Gluster servers %s are not yet detected, "
                     "Make sure tendrl-ansible is executed for the these "
                     "nodes" % list(gluster_fqdn.values())},
                    job_id=self.parameters['job_id'],
                    flow_id=self.parameters['flow_id']
                )
                gluster_server_peer_check = False
        except (
            etcd.EtcdKeyNotFound,
            ValueError,
            TypeError,
            AttributeError,
            IndexError,
            KeyError,
            GlusterServerPeerError
        ) as ex:
            logger.log(
                "error",
                NS.publisher_id,
                {"message": "Unable to compare detected nodes with "
                 "gluster peer list. Error: %s" % ex},
                job_id=self.parameters['job_id'],
                flow_id=self.parameters['flow_id']
            )
            gluster_server_peer_check = False
        return gluster_server_peer_check
