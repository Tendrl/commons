import os

import pkg_resources
from ruamel import yaml

from tendrl.commons.utils import ansible_module_runner
from tendrl.commons.utils import cmd_utils
from tendrl.commons.utils import log_utils as logger


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
        return False

    logger.log(
        "info",
        NS.publisher_id,
        {
            'message': "Installing tendrl-gluster-integration on "
            "Node %s" % NS.node_context.fqdn
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
        if out['rc'] != 0:
            logger.log(
                "error",
                NS.publisher_id,
                {
                    "message": "Could not install "
                    "tendrl-gluster-integration on Node %s"
                    "Error: %s" %
                    (NS.node_context.fqdn, out['msg'])
                },
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
            )
            return False
    except ansible_module_runner.AnsibleExecutableGenerationFailed:
        logger.log(
            "error",
            NS.publisher_id,
            {
                "message": "Error: Could not install "
                "tendrl-gluster-integration on Node %s" %
                NS.node_context.fqdn
            },
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
        )
        return False

    logger.log(
        "info",
        NS.publisher_id,
        {
            "message": "Generating configuration for "
            "tendrl-gluster-integration on Node %s" %
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
            "message": "Running tendrl-gluster-integration on Node "
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
            logger.log(
                "error",
                NS.publisher_id,
                {
                    "message": "Could not enable gluster-integration"
                    " service. Error: %s" % err
                },
                job_id=parameters['job_id'],
                flow_id=parameters['flow_id'],
            )
            return False

    cmd = cmd_utils.Command(_cmd)
    err, out, rc = cmd.run()
    if err:
        logger.log(
            "error",
            NS.publisher_id,
            {
                "message": "Could not start gluster-integration"
                " service. Error: %s" % err
            },
            job_id=parameters['job_id'],
            flow_id=parameters['flow_id'],
        )
        return False

    return True
