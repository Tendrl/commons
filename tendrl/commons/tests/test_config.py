import os

from mock import MagicMock
import pytest

from tendrl.commons import config


class TestConfig(object):
    def test_load_config(self):
        os.path.exists = MagicMock(return_value=True)
        config.load_config("module-name",
            "/etc/tendrl/module-name/module-name.conf.yaml")
        os.path.exists.assert_called_with(
            "/etc/tendrl/module-name/module-name.conf.yaml")
        os.path.exists = MagicMock(return_value=False)
        with pytest.raises(config.ConfigNotFound):
            config.load_config("module-name", "/temp/dummy.conf")
