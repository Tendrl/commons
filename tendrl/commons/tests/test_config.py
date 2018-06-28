import pytest
from tendrl.commons import config
from tendrl.commons import singleton


# Tests that an exception is correctly raised when handed
# a path that does not exist
def test_config():
    with pytest.raises(Exception):
        config.load_config(singleton, "test.yaml")
