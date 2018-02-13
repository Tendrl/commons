import subprocess

import pkg_resources
from ruamel import yaml

from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils import log_utils as logger


def import_ceph(parameters):
    logging_file_name = "ceph-integration_logging.yaml"
    logging_config_file_path = "/etc/tendrl/ceph-integration/"
    attributes = {}
    if NS.config.data['package_source_type'] == 'pip':
        _cmd = "nohup tendrl-ceph-integration &"
        name = "https://github.com/Tendrl/ceph-integration/archive/master" \
               ".tar.gz"
        attributes["name"] = name
        attributes["editable"] = "false"
        ansible_module_path = "packaging/language/pip.py"
    elif NS.config.data['package_source_type'] == 'rpm':
        name = "tendrl-ceph-integration"
        _cmd = "systemctl restart %s" % name
        ansible_module_path = "packaging/os/yum.py"
        attributes["name"] = name
    else:
        return False

    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Installing tendrl-ceph-integration on Node "
                    "%s" % NS.node_context.node_id},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
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
        runner.run()
    except ansible_module_runner.AnsibleExecutableGenerationFailed:
        logger.log(
            "error",
            NS.publisher_id,
            {"message": "Error: Could not install "
                        "tendrl-ceph-integration on Node %s" %
                        NS.node_context.node_id},
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id']
        )

        return False

    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Generating configuration for "
                    "tendrl-ceph-integration on Node %s" %
                    NS.node_context.node_id},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
    )

    with open(logging_config_file_path + logging_file_name,
              'w+') as f:
        f.write(pkg_resources.resource_string(__name__, logging_file_name))

    ceph_integration_tag = NS.compiled_definitions.get_parsed_defs()[
        'namespace.tendrl'
    ]['tags']['tendrl-ceph-integration']

    config_data = {"etcd_port": int(NS.config.data['etcd_port']),
                   "etcd_connection": str(NS.config.data['etcd_connection']),
                   "log_cfg_path": (logging_config_file_path +
                                    logging_file_name),
                   "log_level": "DEBUG",
                   "logging_socket_path": "/var/run/tendrl/message.sock",
                   "sync_interval": 10,
                   "tags": [ceph_integration_tag]}
    with open("/etc/tendrl/ceph-integration/ceph-integration.conf.yaml",
              'w') as outfile:
        yaml.dump(config_data, outfile, default_flow_style=False)

    logger.log(
        "info",
        NS.publisher_id,
        {"message": "Running tendrl-ceph-integration on Node %s" %
                    NS.node_context.node_id},
        job_id=parameters['job_id'],
        flow_id=parameters['flow_id']
    )

    subprocess.Popen(_cmd.split())
