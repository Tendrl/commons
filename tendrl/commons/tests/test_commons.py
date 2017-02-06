"""
test_commons
----------------------------------

Tests for `commons` module.
"""
import sys

from mock import MagicMock

sys.modules['logging'] = MagicMock()
from tendrl.commons import etcdobj
from tendrl.commons.etcdobj import fields


class PytestEtcdObj(etcdobj.EtcdObj):
    """A simple EtcdObj for testing."""
    __name__ = 'unittesting'
    testingInt = fields.IntField('testingInt')
    testdict = fields.DictField("testdict",
        {'value1': str, 'value2': str}, None)


class TestBridge_commons(object):
    def setup_class(self):
        self.Fields = fields
        self.Etcdobj = etcdobj
