from oslo_config import cfg
from oslo_log import log as logging

CONF = cfg.CONF
DOMAIN = "Tendrl"
logging.register_options(CONF)
logging_format = "%(asctime)s.%(msecs)03d %(process)d %(levelname)s" \
                 "%(pathname)s.%(name)s [-] %(instance)s%(message)s"

CONF.set_default("log_dir", default="/var/log/tendrl/")
CONF.set_default("log_file", default="tendrl_bridge_common.log")
CONF.set_default("logging_default_format_string",
                 default=logging_format)


logging.setup(CONF, DOMAIN)
LOG = logging.getLogger(__name__)
