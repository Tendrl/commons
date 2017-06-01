import pytest
from tendrl.commons.utils import import_utils
import importlib
from mock import patch
import mock
import inspect

def test_load_abs_module():
    obj = importlib.import_module("tendrl.commons.tests.fixtures.config")
    module = import_utils.load_abs_module("tendrl.commons.tests.fixtures.config")
    assert obj == module

def test_load_abs_class():
    obj = import_utils.load_abs_class("tendrl.commons.tests.fixtures.config.Config")
    assert inspect.isclass(obj)
