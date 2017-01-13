import os

import mock
from mock import MagicMock
import pytest

from tendrl.commons import config


class TestConfig(object):

    @mock.patch("open", create=True)
    def test_load_config(self, mock_open):
        os.path.exists = MagicMock(return_value=True)
        file_name = "/etc/tendrl/module-name/module-name.conf.yaml"
        config.load_config("module-name", file_name)
        mock_open.assert_called_once_with(file_name)
        os.path.exists.assert_called_with(
            "/etc/tendrl/module-name/module-name.conf.yaml")
        os.path.exists = MagicMock(return_value=False)
        with pytest.raises(config.ConfigNotFound):
            config.load_config("module-name", "/temp/dummy.conf")
