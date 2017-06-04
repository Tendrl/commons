from tendrl.commons import singleton
import sys

def test_to_singleton():
    cls_body = dict(__doc__='docstring', __name__='Dummy class', __module__='modname')
    cls = type('Dummy', (object,), cls_body)
    ret = singleton.to_singleton(cls)
    retClass = ret()
    assert isinstance(retClass,cls)
    ret_class = ret()
