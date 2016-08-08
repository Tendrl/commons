import logging

from bridge_common.config import TendrlConfig
config = TendrlConfig()


FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
log = logging.getLogger('EtcdObj')
handler = logging.FileHandler(config.get('common', 'log_path'))
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
log.setLevel(logging.getLevelName(config.get('common', 'log_level')))
