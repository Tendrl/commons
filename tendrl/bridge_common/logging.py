import logging

from tendrl.bridge_common.config import TendrlConfig
config = TendrlConfig()


FORMAT = "[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s"
root = logging.getLogger()
handler = logging.FileHandler(config.get('bridge_common', 'log_path'))
handler.setFormatter(logging.Formatter(FORMAT))
root.addHandler(handler)
root.setLevel(logging.getLevelName(config.get('bridge_common', 'log_level')))
