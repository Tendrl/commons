# flake8: noqa
import json
import subprocess

from ruamel import yaml

from tendrl.commons.utils import ansible_module_runner

def import_ceph(integration_id):
    attributes = {}
    if NS.config.data['package_source_type'] == 'pip':
        name = "git+https://github.com/Tendrl/ceph-integration/archive/master.tar.gz"
        attributes["name"] = name
        attributes["editable"] = "false"
        ansible_module_path = "core/packaging/language/pip.py"
    elif NS.config.data['package_source_type'] == 'rpm':
        name = "tendrl-ceph-integration"
        ansible_module_path = "core/packaging/os/yum.py"
        attributes["name"] = name
    else:
        return False

    try:
        runner = ansible_module_runner.AnsibleRunner(
            ansible_module_path,
            **attributes
        )
        result, err = runner.run()
    except ansible_module_runner.AnsibleExecutableGenerationFailed:
        return False
    
    with open("/etc/tendrl/ceph-integration/ceph-integration_logging"
                       ".yaml", 'w+') as f:
        f.write(logging_file)

    config_data = {"etcd_port": int(NS.config.data['etcd_port']),
                   "etcd_connection": str(NS.config.data['etcd_connection']),
                   "log_cfg_path":"/etc/tendrl/ceph-integration/ceph-integration_logging"
                       ".yaml", "log_level": "DEBUG",
                       "logging_socket_path": "/var/run/tendrl/message.sock",
                       "tags": json.dumps(["tendrl/integration/ceph"])}
    with open("/etc/tendrl/ceph-integration/ceph-integration"
              ".conf.yaml", 'w') as outfile:
        yaml.dump(config_data, outfile, default_flow_style=False)

    ceph_integration_context = "/etc/tendrl/ceph-integration/integration_id"
    with open(ceph_integration_context, 'wb+') as f:
        f.write(integration_id)

    subprocess.Popen(["nohup", "tendrl-ceph-integration", "&"])










logging_file = """version: 1
disable_existing_loggers: False
formatters:
    simple:
        format: "%(asctime)s - %(pathname)s - %(filename)s:%(lineno)s - %(funcName)20s() - %(levelname)s - %(message)s"
        datefmt: "%Y-%m-%dT%H:%M:%S%z"

handlers:
    console:
        class: logging.StreamHandler
        level: DEBUG
        formatter: simple
        stream: ext://sys.stdout

    info_file_handler:
        class: logging.handlers.TimedRotatingFileHandler
        level: INFO
        formatter: simple
        filename: /var/log/tendrl/ceph-integration/ceph-integration_info.log

    error_file_handler:
        class: logging.handlers.RotatingFileHandler
        level: ERROR
        formatter: simple
        filename: /var/log/tendrl/ceph-integration/ceph-integration_errors.log
        maxBytes: 10485760 # 10MB
        backupCount: 20
        encoding: utf8

loggers:
    my_module:
        level: ERROR
        handlers: [console]
        propagate: no

root:
    level: INFO
    handlers: [console, info_file_handler, error_file_handler]
"""
