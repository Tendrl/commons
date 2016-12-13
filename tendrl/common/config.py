import ConfigParser
import logging
import os

LOG = logging.getLogger(__name__)


class ConfigNotFound(Exception):
    pass


class TendrlConfig(ConfigParser.SafeConfigParser):
    def __init__(self, module, cfg_file_path):
        ConfigParser.SafeConfigParser.__init__(self)

        self.path = cfg_file_path

        if not os.path.exists(self.path):
            err = ConfigNotFound(
                "Configuration for module: %s not found at %s" %
                module, self.path
            )
            LOG.error(err, exc_info=True)
            raise err

        self.read(self.path)
