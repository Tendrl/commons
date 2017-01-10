import logging
import os

import yaml

LOG = logging.getLogger(__name__)


class ConfigNotFound(Exception):
    pass


def load_config(self, module, yaml_cfg_file_path):

        if not os.path.exists(yaml_cfg_file_path):
            err = ConfigNotFound(
                "Configuration for module: %s not found at %s" %
                (module, yaml_cfg_file_path)
            )
            LOG.error(err, exc_info=True)
            raise err

        with open(yaml_cfg_file_path, 'r') as ymlfile:
            return yaml.safe_load(ymlfile)
