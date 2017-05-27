import pytest
from tendrl.commons.utils import import_utils
import importlib
from mock import patch
import mock

def test_load_abs_module():
    obj = importlib.import_module("tendrl.commons.fixtures.config")
    module = import_utils.load_abs_module("tendrl.commons.fixtures.config")
    assert obj == module

def test_load_abs_class():
    with pytest.raises(TypeError):
        obj = import_utils.load_abs_class("tendrl.commons.fixtures.config.Config")
