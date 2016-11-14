import json
from mock import MagicMock
import pytest
from tendrl.common.tests.test_common import PytestEtcdObj
from tendrl.common.tests.test_common import TestBridge_common


class TestEtcdobj(TestBridge_common):
    def setup_method(self, method):
        self.testing_obj = PytestEtcdObj(
            testingInt=10,
            testingDict={'value1': "string1", 'value2': "string2"})
        self.client = MagicMock()
        self.client.get.return_value = True
        self.client.write.return_value = True
        self.client.delete.return_value = True

    def test_ClientCreation(self):
        server = self.Etcdobj._Server(self.client)
        assert self.client == server.client
        with pytest.raises(ValueError):
            self.Etcdobj._Server(bool())
        with pytest.raises(ValueError):
            self.Etcdobj._Server(dict())

    def test_save(self):
        server = self.Etcdobj._Server(self.client)
        server.save(self.testing_obj)
        self.client.write.assert_called_with(
            '/unittesting/testingInt', 10, quorum=True)
        server.save(self.testing_obj)
        self.client.write.assert_called_with(
            '/unittesting/testingInt', 10, quorum=True)

    def test_read(self):
        server = self.Etcdobj._Server(self.client)
        self.client.read.return_value = MagicMock(value="10")
        obj = server.read(self.testing_obj)
        self.client.read.assert_called_with(
            '/unittesting/testingInt', quorum=True)
        assert obj.testingInt == 10
        self.testing_obj = PytestEtcdObj(testingInt="10")
        obj = server.read(self.testing_obj)
        self.client.read.assert_called_with(
            '/unittesting/testingInt', quorum=True)
        assert obj.testingInt == 10


class TestEtcdObj(TestBridge_common):
    def setup_method(self, method):
        self.testing_obj = PytestEtcdObj(
            testingInt=10,
            testingDict={'value1': "string1", 'value2': "string2"})

    def test_render(self):
        item = self.testing_obj.render()
        for obj in item:
            assert(
                {"name": "testingInt", "key": "/unittesting/testingInt",
                 "value": 10, "dir": False} in item)

    def test_json(self):
        assert(json.dumps({"testingDict": {
                           "value1": "string1",
                           "value2": "string2"},
                           "testingInt": 10
                           }) == self.testing_obj.json)
