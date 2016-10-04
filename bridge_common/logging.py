import logging

from bridge_common.config import TendrlConfig
config = TendrlConfig()


FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
handler = logging.FileHandler(config.get('bridge_common', 'log_path'))
handler.setFormatter(logging.Formatter(FORMAT))
log.addHandler(handler)
log.setLevel(logging.getLevelName(config.get('bridge_common', 'log_level')))