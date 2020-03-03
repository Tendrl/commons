import builtins
from mock import patch
import os.path
import pytest
import tempfile

from ruamel import yaml

from tendrl.commons import config
from tendrl.commons import singleton


# Tests that an exception is correctly raised when handed
# a path that does not exist
def test_config1():
    with pytest.raises(Exception):
        config.load_config(singleton, "test.yaml")


# Mocks the file path
@patch.object(os.path, "exists")
@patch.object(yaml, "safe_load")
def test_config2(mock_os_path, mock_yaml):
    f = tempfile.TemporaryFile()
    with patch.object(__builtin__, "open") as mock_open:
        mock_open.return_value = f
        mock_os_path.exists.return_value = True
        mock_yaml.safe_load.return_value = "Test return"
        config.load_config(singleton, "test.yaml")
