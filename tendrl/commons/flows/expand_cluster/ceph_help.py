import json
import socket
import uuid

from tendrl.commons.event import Event
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.flows.create_cluster import \
    ceph_help as create_ceph_help
from tendrl.commons.message import Message
from tendrl.commons.objects.job import Job


def expand_cluster(parameters):
    # install the packages
    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Installing Ceph Packages %s" %
                                parameters['TendrlContext.integration_id']
                     }
        )
    )
    mon_ips, osd_ips = create_ceph_help.install_packages(parameters)

    # Get the list of existing mons
    created_mons = existing_mons(parameters)

    # If mons passed create add them
    if len(mon_ips) > 0:
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Creating Ceph Monitors %s" %\
                    parameters['TendrlContext.integration_id']
                }
            )
        )
        created_mons = create_mons(parameters, mon_ips, created_mons)

    # If osds passed create and add them
    if len(osd_ips) > 0:
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Creating Ceph OSD %s" %\
                    parameters['TendrlContext.integration_id']
                }
            )
        )
        create_ceph_help.create_osds(parameters, created_mons)
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Created OSD on Cluster %s" %\
                    parameters['TendrlContext.integration_id']
                }
            )
        )


def create_mons(parameters, mon_ips, created_mons):
    plugin = NS.ceph_provisioner.get_plugin()
    mon_secret = NS._int.client.read(
        "clusters/%s/_mon_key" % parameters['TendrlContext.integration_id']
    ).value
    for mon_ip in mon_ips:
        mon_host_name = socket.gethostbyaddr(mon_ip)[0]
        task_id = plugin.configure_mon(
            mon_host_name,
            parameters['TendrlContext.cluster_id'],
            parameters["TendrlContext.cluster_name"],
            mon_ip,
            parameters["Cluster.cluster_network"],
            parameters["Cluster.public_network"],
            created_mons,
            mon_secret=mon_secret
        )
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={
                    "message": "Creating Ceph MON %s, ceph-installer task %s" %\
                    (mon_ip, task_id)
                }
            )
        )

        create_ceph_help.wait_for_task(task_id)
        created_mons.append({"address":mon_ip, "host": mon_ip})
    return created_mons


def existing_mons(parameters):
    mons = NS._int.client.read(
        "clusters/%s/maps/mon_map/data/mons" %\
        parameters["TendrlContext.integration_id"]
    ).value

    created_mons = []
    for mon in json.loads(mons.replace("'", '"')):
        mon_ip = mon['addr'].split(':')[0]
        mon_host_name = socket.gethostbyaddr(mon_ip)[0]
        created_mons.append(
            {
                "address": mon_ip,
                "host": mon_host_name
            }
        )

    return created_mons
