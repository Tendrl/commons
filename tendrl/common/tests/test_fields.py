import datetime
import json
import pytest
from tendrl.common.tests.test_common import TestBridge_common


class TestField(TestBridge_common):
    def setup_method(self, method):
        self.obj = self.Fields.Field("unittesting")

    def test_instance_creation(self):
        """Verify creation of instance works as expected.

        """
        assert self.obj.name == "unittesting"
        assert self.obj._value is None

    def test_value(self):
        assert self.obj._value is None
        self.obj.value = 10
        assert self.obj._value == 10
        self.obj.value = "testing"
        assert self.obj._value == "testing"
        self.obj.value = 0.123
        assert self.obj._value != 100
        assert self.obj._value == 0.123

    def test_json(self):
        """Verify creation of json works as expected.

        """
        assert json.dumps({"unittesting": None}) == self.obj.json
        self.obj.value = 10
        assert json.dumps({"unittesting": 10}) == self.obj.json
        self.obj.value = None
        self.obj.name = None
        assert json.dumps({None: None}) == self.obj.json
        self.obj.value = 100
        self.obj.name = "testing"
        assert json.dumps({"testing": 100}) == self.obj.json

    def test_render(self):
        """Verify rendering  works as expected.

        """
        structure = {"name": "unittesting",
                     "key": "unittesting",
                     "value": None,
                     "dir": False
                     }
        assert structure == self.obj.render()
        self.obj.name = "testing"
        self.obj.value = 10
        structure = {"name": "testing",
                     "key": "testing",
                     "value": 10,
                     "dir": False
                     }
        assert structure == self.obj.render()
        self.obj.name = 1
        self.obj.value = 10
        structure = {"name": 1,
                     "key": 1,
                     "value": 10,
                     "dir": False
                     }
        self.obj.name = None
        self.obj.value = None
        structure = {"name": None,
                     "key": None,
                     "value": None,
                     "dir": False
                     }
        assert structure == self.obj.render()


class TestIntField(TestBridge_common):
    def setup_method(self, method):
        self.obj = self.Fields.IntField("unittesting")

    def test_intCastField(self):
        self.obj.value = "10"
        assert self.obj._value == 10
        self.obj.value = "-1"
        assert self.obj._value == -1
        with pytest.raises(ValueError):
            self.obj.value = "testing"


class TestStrField(TestBridge_common):
    def setup_method(self, method):
        self.obj = self.Fields.StrField("unittesting")

    def test_strCastField(self):
        self.obj.value = 10
        assert self.obj._value == "10"
        self.obj.value = -1
        assert self.obj._value == "-1"
        self.obj.value = 'testing'
        assert self.obj._value == "testing"
        self.obj.value = 0.123
        assert self.obj._value == "0.123"


class TestDateTimeField(TestBridge_common):
    def setup_method(self, method):
        self.obj = self.Fields.DateTimeField('unittesting', '%Y-%m-%d')

    def test_dateCastingField(self):
        self.obj.value = '1993-5-26'
        assert datetime.datetime(1993, 5, 26) == self.obj._value
        with pytest.raises(ValueError):
            self.obj.value = "Invalid date formate"
        with pytest.raises(ValueError):
            self.obj.value = '93-5-26'
        with pytest.raises(ValueError):
            self.obj.value = '1993/05/26'
        self.obj.value = datetime.datetime(2016, 10, 12)
        assert datetime.datetime(2016, 10, 12) == self.obj._value

    def test_json(self):
        self.obj.value = '1993-5-26'
        value = datetime.datetime(1993, 5, 26)
        value = datetime.datetime.strftime(value, '%Y-%m-%d')
        assert json.dumps({"unittesting": value}) == self.obj.json

    def test_render(self):
        self.obj.value = '1993-05-26'
        value = datetime.datetime(1993, 5, 26)
        value = datetime.datetime.strftime(value, '%Y-%m-%d')
        assert(
            {"name": "unittesting",
             "key": "unittesting",
             "value": value,
             "dir": False} == self.obj.render())


class Test_DictField(TestBridge_common):
    def setup_method(self, method):
        self.obj = self.Fields.DictField(
            'unittesting', {'value1': int, 'value2': str})

    def test_dictCastingField(self):
        self.obj.value = {'value1': "10", 'value2': 10}
        assert self.obj._value == {'value1': 10, 'value2': "10"}
        with pytest.raises(ValueError):
            self.obj.value = {'value1': "testing", 'value2': 10}
        with pytest.raises(TypeError):
            self.obj.value = "InvalidDictValue"

    def test_json(self):
        self.obj.value = {'value1': "10", 'value2': 10}
        assert(
            json.dumps({"value1": 10, "value2": "10"}) == self.obj.json)

    def test_render(self):
        self.obj.value = {'value1': "10", 'value2': 10}
        testing_obj = [{"name": "unittesting",
                        "key": "unittesting/value1",
                        "value": 10,
                        "dir": True},
                       {"name": "unittesting",
                        "key": "unittesting/value2",
                        "value": "10",
                        "dir": True}]
        for obj in testing_obj:
            assert(obj in self.obj.render())
