import os
import subprocess
import time

import pkg_resources
from ruamel import yaml

from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils import log_utils as logger
from tendrl.commons.utils.service_status import ServiceStatus


def import_gluster(parameters):
    logging_file_name = "gluster-integration_logging.yaml"
    logging_config_file_path = "/etc/tendrl/gluster-integration/"

    attributes = {}
    if NS.config.data['package_source_type'] == 'pip':
        _cmd = "nohup tendrl-gluster-integration &"
        name = "https://github.com/Tendrl/gluster-integration/archive/master" \
               ".tar.gz"
        attributes["name"] = name
        attributes["editable"] = "false"
        ansible_module_path = "packaging/language/pip.py"
    elif NS.config.data['package_source_type'] == 'rpm':
        name = "tendrl-gluster-integration"
        _cmd = "systemctl restart %s" % name
        ansible_module_path = "packaging/os/yum.py"
        attributes["name"] = name
    else:
        return (
            False,
            "Invalid package_source_type: %s" %
            NS.config.data['package_source_type']
        )

    logger.log(
        "info",
        NS.publisher_id,
        {
            'message': "Installing tendrl-gluster-integration on "
            "%s" % NS.node_context.fqdn
        },
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id'],
    )

    try:
        runner = ansible_module_runner.AnsibleRunner(
            ansible_module_path,
            **attributes
        )
    except ansible_module_runner.AnsibleModuleNotFound:
        # Backward compat ansible<=2.2
        runner = ansible_module_runner.AnsibleRunner(
            "core/" + ansible_module_path,
            **attributes
        )
    try:
        out, err = runner.run()
        if type(out) is dict and out.get('rc', 1) != 0:
            err_msg = "Could not install tendrl-gluster-integration " \
                "on %s. Error: %s" % (NS.node_context.fqdn, out.get('msg', ''))
            logger.log(
                "error",
                NS.publisher_id,
                {"message": err_msg},
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
            )
            return False, err_msg
    except ansible_module_runner.AnsibleExecutableGenerationFailed:
        err_msg = "Cluster management requires service " \
            "tendrl-gluster-integration. Failed to install same" \
            "on Node %s" % NS.node_context.fqdn
        logger.log(
            "error",
            NS.publisher_id,
            {"message": err_msg},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
        )
        return False, err_msg

    logger.log(
        "info",
        NS.publisher_id,
        {
            "message": "Generating tendrl-gluster-integration "
            "configuration on %s" %
            NS.node_context.fqdn
        },
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id'],
    )

    with open(logging_config_file_path + logging_file_name,
              'w+') as f:
        f.write(pkg_resources.resource_string(__name__, logging_file_name))
    gluster_integration_tag = NS.compiled_definitions.get_parsed_defs()[
        'namespace.tendrl'
    ]['tags']['tendrl-gluster-integration']
    config_data = {
        "etcd_port": int(NS.config.data['etcd_port']),
        "etcd_connection": str(NS.config.data['etcd_connection']),
        "log_cfg_path": (logging_config_file_path +
                         logging_file_name),
        "log_level": "DEBUG",
        "logging_socket_path": "/var/run/tendrl/message.sock",
        "sync_interval": int(NS.config.data['sync_interval']),
        "tags": [gluster_integration_tag]
    }
    etcd_ca_cert_file = NS.config.data.get("etcd_ca_cert_file")
    etcd_cert_file = NS.config.data.get("etcd_cert_file")
    etcd_key_file = NS.config.data.get("etcd_key_file")
    if etcd_ca_cert_file and str(
            etcd_ca_cert_file
    ) != "" and etcd_cert_file and str(
        etcd_cert_file
    ) != "" and etcd_key_file and str(
        etcd_key_file
    ) != "":
        config_data.update({
            "etcd_ca_cert_file": NS.config.data['etcd_ca_cert_file'],
            "etcd_cert_file": NS.config.data['etcd_cert_file'],
            "etcd_key_file": NS.config.data['etcd_key_file']
        })

    _gluster_integration_conf_file_path = \
        "/etc/tendrl/gluster-integration/gluster-integration.conf.yaml"
    with open(_gluster_integration_conf_file_path,
              'w') as outfile:
        yaml.dump(config_data, outfile, default_flow_style=False)
    logger.log(
        "info",
        NS.publisher_id,
        {
            "message": "Running tendrl-gluster-integration on "
            "%s" % NS.node_context.fqdn
        },
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id'],
    )
    os.chmod(_gluster_integration_conf_file_path, 0o640)

    if NS.config.data['package_source_type'] == 'rpm':
        command = cmd_utils.Command(
            "systemctl enable tendrl-gluster-integration"
        )
        err, out, rc = command.run()
        if err:
            err_msg = "Could not enable tendrl-gluster-integration " \
                "service. Error: %s" % err
            logger.log(
                "error",
                NS.publisher_id,
                {"message": err_msg},
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
            )
            return False, err_msg

    cmd = cmd_utils.Command(_cmd)
    err, out, rc = cmd.run()
    if err:
        err_msg = "Could not start tendrl-gluster-integration " \
            "service. Error: %s" % err
        logger.log(
            "error",
            NS.publisher_id,
            {"message": err_msg},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
        )
        return False, err_msg

    # Check if tendrl-gluster-integration active on the node
    response = ServiceStatus(
        "tendrl-gluster-integration"
    ).status()
    if not response:
        return (
            False,
            "Cluster management requires service tendrl-gluster-integration."
            " The same is not running on node: %s" %
            NS.node_context.fqdn
        )

    return True, ""


def enable_disable_volume_profiling(volumes, parameters):
    try:
        cluster = NS.tendrl.objects.Cluster(
            integration_id=NS.tendrl_context.integration_id
        ).load()
        # Enable / disable based on cluster flag volume_profiling_flag
        # should be done only once while first sync. Later the volume
        # level volume_profiling_state should be set based on individual
        # volume level values
        if cluster.volume_profiling_flag == "enable":
            logger.log("info",
                       NS.publisher_id,
                       {"message": "Starting profiling for volumes"},
                       job_id=parameters['job_id'],
                       flow_id=parameters['flow_id']
                       )
            for volume in volumes:
                p = subprocess.Popen(
                    ["gluster",
                     "volume",
                     "profile",
                     volume,
                     "start"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                retry = 1
                while True:
                    if p.poll() is not None:
                        break
                    elif retry > 10 and p.poll() is None:
                        p.kill()
                        break
                    retry += 1
                    time.sleep(0.5)
        if cluster.volume_profiling_flag == "disable":
            logger.log("info",
                       NS.publisher_id,
                       {"message": "Stopping profiling for volumes"},
                       job_id=parameters['job_id'],
                       flow_id=parameters['flow_id']
                       )
            for volume in volumes:
                p = subprocess.Popen(
                    ["gluster",
                     "volume",
                     "profile",
                     volume,
                     "stop"],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                retry = 1
                while True:
                    if p.poll() is not None:
                        break
                    elif retry > 10 and p.poll() is None:
                        p.kill()
                        break
                    retry += 1
                    time.sleep(0.5)
        return True, ""
    except Exception as ex:
        return False, str(ex)
