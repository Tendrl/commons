import logging
import os
import yaml


def setup_logging(
    log_cfg_path='/etc/tendrl/logging.yaml',
    default_log_level=logging.INFO
):
    """Setup logging configuration

    """
    if os.path.exists(log_cfg_path):
        with open(log_cfg_path, 'rt') as f:
            log_config = yaml.safe_load(f.read())
        logging.config.dictConfig(log_config)
    else:
        raise Exception("logging configuration not found")
