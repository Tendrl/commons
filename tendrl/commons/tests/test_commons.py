"""
test_commons
----------------------------------

Tests for `commons` module.
"""
import sys

from mock import MagicMock

sys.modules['logging'] = MagicMock()
from tendrl.commons.etcdobj import etcdobj
from tendrl.commons.etcdobj import fields


class PytestEtcdObj(etcdobj.EtcdObj):
    """A simple EtcdObj for testing."""
    __name__ = 'unittesting'
    testingInt = fields.IntField('testingInt')
    testingDict = fields.DictField(
        'testingDict', {'value1': str, 'value2': str})


class TestBridge_commons(object):
    def setup_class(self):
        self.Fields = fields
        self.Etcdobj = etcdobj
