# flake8: noqa
import gevent
from tendrl.commons.flows.exceptions import FlowExecutionFailedError


def create_ceph(parameters):
    # install the packages
    mon_ips, osd_ips = install_packages(parameters)
    # Configure Mons
    created_mons = create_mons(parameters, mon_ips)
    # Configure osds
    create_osds(parameters, created_mons)


def install_packages(parameters):
    plugin = NS.provisioner.get_plugin()
    mon_ips = []
    osd_ips = []
    for node, config in parameters["node_configuration"].iteritems():
        if "mon" in config["role"].lower():
            mon_ips.append(config["provisioning_ip"])
        elif "osd" in config["role"].lower():
            osd_ips.append(config["provisioning_ip"])

    task_id = plugin.install_mon(mon_ips)
    status, err = sync_task_status(task_id)
    if not status:
        raise FlowExecutionFailedError(err)
    task_id = plugin.install_osd(osd_ips)
    status, err = sync_task_status(task_id)
    if not status:
        raise FlowExecutionFailedError(err)
    return mon_ips, osd_ips

def create_mons(parameters, mon_ips):
    created_mons = []
    plugin = NS.provisioner.get_plugin()
    for mon_ip in mon_ips:
            task_id = plugin.configure_mon(mon_ip,
                                           parameters["TendrlContext.integration_id"],
                                           parameters["name"],
                                           parameters["cluster_network"],
                                           parameters["public_network"],
                                           created_mons
                                           )
            status, err = sync_task_status(task_id)
            if not status:
                raise FlowExecutionFailedError(err)
            else:
                # If success add the MON to the created list
                created_mons.append({"address":mon_ip, "host": mon_ip})
    return created_mons


def create_osds(parameters, created_mons):
    failed = []
    plugin = NS.provisioner.get_plugin()
    for node, config in parameters["node_configuration"].iteritems():
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
                    parameters["TendrlContext.integration_id"],
                    parameters["name"],
                    config["journal_size"],
                    parameters["cluster_network"],
                    parameters["public_network"],
                    created_mons
                    )
                status, err = sync_task_status(task_id)
                if not status:
                    raise FlowExecutionFailedError(err)


def sync_task_status(task_id):
    status = False
    count = 0
    plugin = NS.provisioner.get_plugin()
    resp = {}
    while count < 90:
        gevent.sleep(10)
        resp = plugin.task_status(task_id)
        if resp:
            if resp["ended"]:
                if resp["succeeded"]:
                    return True, ""
    return status, resp.get("stderr", "ceph-installer task_id %s timed out"
                            % task_id)