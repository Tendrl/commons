from tendrl.common.singleton import to_singleton


@to_singleton
class A(object):
    def __init__(self):
        pass


class TestSingleton(object):
    def test_singleton(self, monkeypatch):
        assert id(A()) == id(A())
