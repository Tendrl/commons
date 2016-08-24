from oslo_config import cfg
from oslo_log import log as logging

LOG = logging.getLogger(__name__)
CONF = cfg.CONF
DOMAIN = "Tendrl"

logging.register_options(CONF)
logging.setup(CONF, DOMAIN)
