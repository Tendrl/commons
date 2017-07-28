import importlib
import inspect
from mock import patch

from tendrl.commons.tests.fixtures.config import Config
from tendrl.commons.utils import import_utils


def test_load_abs_module():
    obj = importlib.import_module("tendrl.commons.tests.fixtures.config")
    module = import_utils.load_abs_module(
        "tendrl.commons.tests.fixtures.config")
    assert obj == module


def test_load_abs_class():
    obj = import_utils.load_abs_class(
        "tendrl.commons.tests.fixtures.config.Config")
    assert inspect.isclass(obj)
    test_ins = obj()
    assert isinstance(test_ins, Config)
    with patch.object(inspect, 'getmembers', return_value=""):
        obj = import_utils.load_abs_class(
            "tendrl.commons.tests.fixtures.config.Config")
        assert obj is None
    with patch.object(inspect, 'getmembers', return_value=[("class", "test")]):
        obj = import_utils.load_abs_class(
            "tendrl.commons.tests.fixtures.config.Config")
        assert obj is None
