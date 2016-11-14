from mock import MagicMock
import pytest
from tendrl.common import config


class TestTendrlconfig(object):
    def setup_method(self, method):
        config.os.path.exists = MagicMock(return_value=True)

    def test_Tendrlconfig(self, monkeypatch):
        config.TendrlConfig()
        config.os.path.exists.assert_called_with("/etc/tendrl/tendrl.conf")
        monkeypatch.setattr(config.os, 'environ', {"TENDRL_CONFIG": "/temp/"})
        config.TendrlConfig()
        config.os.path.exists.assert_called_with("/temp/")
        config.os.path.exists = MagicMock(return_value=False)
        with pytest.raises(config.ConfigNotFound):
            config.TendrlConfig()
