# flake8: noqa
import etcd
import gevent
import json

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
        task_id = plugin.configure_mon(
            mon_ip,
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
                payload={
                    "message": "Creating Ceph MON %s, ceph-installer task %s" %
                    (mon_ip, task_id)
                }
            )
        )

        wait_for_task(task_id)
        created_mons.append({"address":mon_ip, "host": mon_ip})

    # Save the monitor secret for future reference
    if parameters.get('create_mon_secret', False):
        NS._int.wclient.write(
            "clusters/%s/_mon_key" % parameters['TendrlContext.integration_id'],
            plugin.monitor_secret
        )

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

            journal_details = {}
            try:
                journal_details = json.loads(NS._int.client.read(
                    'clusters/%s/JournalDetails/%s/data' % (
                        parameters['TendrlContext.integration_id'],
                        node
                    )
                ).value.decode('utf-8'))
            except etcd.EtcdKeyNotFound:
                pass

            if config["journal_colocation"]:
                for entry in devices:
                    journal_details[entry] = {
                        'journal_count': 1,
                        'ssd': False,
                        'journal_size': config['journal_size'] * 1024 * 1024
                    }
            else:
                for k, v in devices.iteritems():
                    journal_disk_name = v
                    if journal_disk_name in journal_details.keys():
                        journal_details[journal_disk_name]['journal_count'] += 1
                        journal_details[journal_disk_name]['ssd'] = True
                    else:
                        journal_details[journal_disk_name] = {
                            'journal_count': 1,
                            'ssd': False,
                            'journal_size': config['journal_size'] * 1024 * 1024
                        }

            NS.integrations.ceph.objects.Journal(
                integration_id=parameters['TendrlContext.integration_id'],
                node_id=node,
                data=json.dumps(journal_details)
            ).save(update=False)


def wait_for_task(task_id):
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
                else:
                    stderr = resp.get("stderr", "ceph-installer task_id %s failed and did not complete" % task_id)
                    stdout = resp.get("stdout", "")
                    raise FlowExecutionFailedError(dict(ceph_installer_task_id=task_id, ceph_installer_task_stdout=stdout,
                                        ceph_installer_task_stderr=stderr))
        count = count + 1
    stderr = resp.get("stderr", "ceph-installer task_id %s timed out and did not complete" % task_id)
    stdout = resp.get("stdout", "")
    raise FlowExecutionFailedError(dict(ceph_installer_task_id=task_id, ceph_installer_task_stdout=stdout,
                                        ceph_installer_task_stderr=stderr))
