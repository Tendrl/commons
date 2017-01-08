import pytest
from mock import MagicMock

from tendrl.commons import config


class TestTendrlconfig(object):
    def setup_method(self, method):
        config.os.path.exists = MagicMock(return_value=True)

    def test_Tendrlconfig(self, monkeypatch):
        config.TendrlConfig("module", "/etc/tendrl/tendrl.conf")
        config.os.path.exists.assert_called_with("/etc/tendrl/tendrl.conf")
        monkeypatch.setattr(config.os, 'environ', {"TENDRL_CONFIG": "/temp/"})
        config.os.path.exists = MagicMock(return_value=False)
        with pytest.raises(config.ConfigNotFound):
            config.TendrlConfig("module", "/temp/dummy.conf")
