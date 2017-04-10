# flake8: noqa
import gevent

from tendrl.commons.event import Event
from tendrl.commons.flows.exceptions import FlowExecutionFailedError
from tendrl.commons.message import Message

def create_ceph(parameters):
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
    mon_ips, osd_ips = install_packages(parameters)
    # Configure Mons
    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Creating Ceph Monitors %s" %
                                parameters['TendrlContext.integration_id']
                     }
        )
    )

    created_mons = create_mons(parameters, mon_ips)
    # Configure osds
    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Creating Ceph OSD %s" % parameters['TendrlContext.integration_id']}
        )
    )
    create_osds(parameters, created_mons)
    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Created Ceph Cluster %s" % parameters['TendrlContext.integration_id']}
        )
    )

def install_packages(parameters):
    plugin = NS.ceph_provisioner.get_plugin()
    mon_ips = []
    osd_ips = []
    for node, config in parameters["Cluster.node_configuration"].iteritems():
        if "mon" in config["role"].lower():
            mon_ips.append(config["provisioning_ip"])
        elif "osd" in config["role"].lower():
            osd_ips.append(config["provisioning_ip"])

    task_id = plugin.install_mon(mon_ips)
    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Installing Ceph Packages on MONS [%s], ceph-installer task %s" %
                                (" ".join(mon_ips), task_id)
                     }
        )
    )

    wait_for_task(task_id)
    task_id = plugin.install_osd(osd_ips)
    Event(
        Message(
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Installing Ceph Packages on OSDS [%s], ceph-installer task %s" %
                                (" ".join(osd_ips), task_id)
                     }
        )
    )

    wait_for_task(task_id)
    return mon_ips, osd_ips

def create_mons(parameters, mon_ips):
    created_mons = []
    plugin = NS.ceph_provisioner.get_plugin()
    for mon_ip in mon_ips:
        task_id = plugin.configure_mon(mon_ip,
                                           parameters['TendrlContext.cluster_id'],
                                           parameters["TendrlContext.cluster_name"],
                                           mon_ip,
                                           parameters["Cluster.cluster_network"],
                                           parameters["Cluster.public_network"],
                                           created_mons
                                           )
        Event(
            Message(
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
                priority="info",
                publisher=NS.publisher_id,
                payload={"message": "Creating Ceph MON %s, ceph-installer task %s" %
                                    (mon_ip, task_id)
                         }
            )
        )

        wait_for_task(task_id)
        else:
            # If success add the MON to the created list
            created_mons.append({"address":mon_ip, "host": mon_ip})
    return created_mons


def create_osds(parameters, created_mons):
    failed = []
    plugin = NS.ceph_provisioner.get_plugin()
    for node, config in parameters["Cluster.node_configuration"].iteritems():
        if "osd" in config["role"].lower():
            if config["journal_colocation"]:
                devices = []
            else:
                devices = {}
            for device in config["storage_disks"]:
                if config["journal_colocation"]:
                    devices.append(device["device"])
                else:
                    devices[device["device"]] = device["journal"]
            task_id = plugin.configure_osd(
            config["provisioning_ip"],
            devices,
            parameters["TendrlContext.cluster_id"],
            parameters["TendrlContext.cluster_name"],
            config["journal_size"],
            parameters["Cluster.cluster_network"],
            parameters["Cluster.public_network"],
            created_mons
            )
            Event(
                Message(
                    job_id=parameters['job_id'],
                    flow_id=parameters['flow_id'],
                    priority="info",
                    publisher=NS.publisher_id,
                    payload={"message": "Creating Ceph OSD %s, ceph-installer task %s" %
                                        (config["provisioning_ip"], task_id)
                             }
                )
            )

            wait_for_task(task_id)

def wait_for_task(task_id):
    status = False
    count = 0
    plugin = NS.ceph_provisioner.get_plugin()
    resp = {}
    while count < 90:
        gevent.sleep(10)
        resp = plugin.task_status(task_id)
        if resp:
            if resp["ended"]:
                if resp["succeeded"]:
                    return
    stderr = resp.get("stderr", "ceph-installer task_id %s timed out and did not complete" % task_id)
    stdout = resp.get("stdout", "")
    raise FlowExecutionFailedError(dict(stdout=stdout, stderr=stderr))
