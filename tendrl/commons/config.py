import os

from ruamel import yaml

from tendrl.commons.event import Event
from tendrl.commons.message import Message


class ConfigNotFound(Exception):
    pass


def load_config(module, yaml_cfg_file_path):
    if not os.path.exists(yaml_cfg_file_path):
        err = ConfigNotFound(
            "Configuration for module: %s not found at %s" %
            (module, yaml_cfg_file_path)
        )
        Event(
            Message(
                priority="error",
                publisher=tendrl_ns.publisher_id,
                payload={"message": err}
            )
        )
        raise err

    with open(yaml_cfg_file_path, 'r') as ymlfile:
        return yaml.safe_load(ymlfile)
