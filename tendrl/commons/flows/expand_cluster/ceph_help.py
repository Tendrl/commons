import json
import socket

from tendrl.commons.flows.create_cluster import \
    ceph_help as create_ceph_help
from tendrl.commons.utils import log_utils as logger


def expand_cluster(parameters):
    # install the packages
    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Installing Ceph Packages %s" %
                    parameters['TendrlContext.integration_id']},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
    )
    mon_ips, osd_ips = create_ceph_help.install_packages(parameters)

    # Get the list of existing mons
    created_mons = existing_mons(parameters)

    # If mons passed create add them
    if len(mon_ips) > 0:
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Creating Ceph Monitors %s" %
             parameters['TendrlContext.integration_id']},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id']
        )
        created_mons = create_mons(parameters, mon_ips, created_mons)

    # If osds passed create and add them
    if len(osd_ips) > 0:
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Creating Ceph OSD %s" %
             parameters['TendrlContext.integration_id']},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id']
        )
        create_ceph_help.create_osds(parameters, created_mons)
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Created OSD on Cluster %s" %
             parameters['TendrlContext.integration_id']},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id']
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
        logger.log(
            "info",
            NS.publisher_id,
            {"message": "Creating Ceph MON %s, ceph-installer task "
                        "%s" % (mon_ip, task_id)},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id']
        )
        create_ceph_help.wait_for_task(task_id)
        created_mons.append({"address": mon_ip, "host": mon_ip})
    return created_mons


def existing_mons(parameters):
    mons = json.loads(
        NS._int.client.read(
            "clusters/%s/maps/mon_map/data" %
            parameters["TendrlContext.integration_id"]
        ).value
    )['mons']

    created_mons = []
    for mon in mons:
        mon_ip = mon['addr'].split(':')[0]
        mon_host_name = socket.gethostbyaddr(mon_ip)[0]
        created_mons.append(
            {
                "address": mon_ip,
                "host": mon_host_name
            }
        )

    return created_mons
