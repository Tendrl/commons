import os
import sys
from ruamel import yaml

class ConfigNotFound(Exception):
    pass


def load_config(module, yaml_cfg_file_path):
    if not os.path.exists(yaml_cfg_file_path):
        err = ConfigNotFound(
            "Configuration for module: %s not found at %s" %
            (module, yaml_cfg_file_path)
        )
        sys.stderr.write(str(err))
        raise err

    with open(yaml_cfg_file_path, 'r') as ymlfile:
        return yaml.safe_load(ymlfile)
