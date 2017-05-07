# flake8: noqa
import json
import subprocess

import pkg_resources
from ruamel import yaml

from tendrl.commons.event import Event
from tendrl.commons.message import Message
from tendrl.commons.utils import ansible_module_runner

def import_gluster(parameters):
    logging_file_name = "gluster-integration_logging.yaml"
    logging_config_file_path = "/etc/tendrl/gluster-integration/"

    attributes = {}
    if NS.config.data['package_source_type'] == 'pip':
        _cmd = "nohup tendrl-gluster-integration &"
        name = "https://github.com/Tendrl/gluster-integration/archive/master.tar.gz"
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

    Event(
        Message(
        job_id=parameters['job_id'],
        flow_id = parameters['flow_id'],
        priority="info",
        publisher=NS.publisher_id,
        payload={"message": "Installing tendrl-gluster-integration on Node %s" % NS.node_context.node_id
             }
    )
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
        Event(
            Message(
            job_id=parameters['job_id'],
            flow_id = parameters['flow_id'],
            priority="info",
            publisher=NS.publisher_id,
            payload={"message": "Error: Could not install tendrl-gluster-integration on Node %s" % NS.node_context.node_id
                 }
        )
        )

        return False

    Event(
        Message(
        job_id=parameters['job_id'],
        flow_id = parameters['flow_id'],
        priority="info",
        publisher=NS.publisher_id,
        payload={"message": "Generating configuration for tendrl-gluster-integration on Node %s" % NS.node_context.node_id
             }
    )
    )

    with open(logging_config_file_path + logging_file_name,
              'w+') as f:
        f.write(pkg_resources.resource_string(__name__, logging_file_name))
    gluster_integration_tag = NS.compiled_definitions.get_parsed_defs()[
        'namespace.tendrl'
    ]['tags']['tendrl-gluster-integration']
    config_data = {"etcd_port": int(NS.config.data['etcd_port']),
                   "etcd_connection": str(NS.config.data['etcd_connection']),
                   "log_cfg_path": logging_config_file_path +
                                   logging_file_name,
                   "log_level": "DEBUG",
                    "logging_socket_path": "/var/run/tendrl/message.sock",
                    "tags": [gluster_integration_tag]}
    with open("/etc/tendrl/gluster-integration/gluster-integration.conf.yaml",
              'w') as outfile:
        yaml.dump(config_data, outfile, default_flow_style=False)
    Event(
        Message(
        job_id=parameters['job_id'],
        flow_id = parameters['flow_id'],
        priority="info",
        publisher=NS.publisher_id,
        payload={"message": "Running tendrl-gluster-integration on Node %s" % NS.node_context.node_id
             }
    )
    )

    subprocess.Popen(_cmd.split())
