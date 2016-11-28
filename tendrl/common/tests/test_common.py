"""
test_common
----------------------------------

Tests for `common` module.
"""
from mock import MagicMock
import sys
sys.modules['logging'] = MagicMock()
from tendrl.common.etcdobj import etcdobj
from tendrl.common.etcdobj import fields


class PytestEtcdObj(etcdobj.EtcdObj):
    """A simple EtcdObj for testing."""
    __name__ = 'unittesting'
    testingInt = fields.IntField('testingInt')
    testingDict = fields.DictField(
        'testingDict', {'value1': str, 'value2': str})


class TestBridge_common(object):

    def setup_class(self):
        self.Fields = fields
        self.Etcdobj = etcdobj
