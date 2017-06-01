import pytest
import __builtin__
from tendrl.commons.utils.central_store.fields import Field
from tendrl.commons.utils.central_store.fields import DateTimeField
from tendrl.commons.utils.central_store.fields import ListField
from tendrl.commons.utils.central_store.fields import DictField
import datetime


'''Unit Test cases for class Field'''


def test_constructor():
    field = Field("test_field")
    assert field.name == "test_field"
    field = Field("test_field",1)
    assert field._value == 1


def test_json():
    field_obj = Field("test_field",2)
    ret = field_obj.json
    assert ret.find("test_field")


def test_value_property():
    field_obj = Field("test_field",2)
    ret = field_obj.value
    assert ret == 2


def test_value_setter():
    field_obj = Field("test_field",2)
    field_obj.value = 5
    assert field_obj._value == 5


def test_render():
    field_obj = Field("test_field",2)
    ret = field_obj.render()
    assert ret["name"] == "test_field"
    assert ret["value"] == 2


'''Unit Test cases for class DateTimeField'''


def test_DateTimeField_constructor():
    date_time_field = DateTimeField("Test_date",datetime.date(2008, 3, 12))
    assert date_time_field._value ==datetime.date(2008, 3, 12)


def test_DateTimeField_json():
    date_time_field = DateTimeField("Test_date",datetime.date(2008, 3, 12))
    ret = date_time_field.json
    assert ret.find("test_date")


def test_DateTimeField_render():
    date_time_field = DateTimeField("Test_date",datetime.date(2008, 3, 12))
    ret = date_time_field.render()
    assert ret["name"] == "Test_date"

'''Unit Test cases for class ListField'''


def test_ListField_constructor():
    list_field = ListField("Test_listfield",[1,2,3])
    assert list_field._value == [1,2,3]


def test_ListField_json():
    list_field = ListField("Test_listfield",[1,2,3])
    ret = list_field.json
    assert ret.find("Test_listfield")


def test_ListField_render():
    list_field = ListField("Test_listfield",[1,2,3])
    ret = list_field.render()
    assert ret["name"] == "Test_listfield"

'''Unit Test cases for class DictField'''


def test_DictField_constructor():
    dict_field = DictField("Test_Dict",{'test':'message'})
    assert dict_field._caster == {'str': 'str'}
    dict_field = DictField("Test_Dict",1,{'int','str'})
    assert dict_field._value == 1
    assert dict_field._caster == {'int','str'}


def test_DictField_json():
    dict_field = DictField("Test_Dict",{'test':'message'})
    ret = dict_field.json
    assert ret is not None


def test_DictField_render():
    dict_field = DictField("Test_Dict",{'test':'message'})
    ret = dict_field.render()
    assert len(ret) > 0
    
def test_DictField__set_value():
    dict_field = DictField("Test_Dict",{'message':'test'})
    dict_field._caster = None
    dict_field._set_value({'message':'test'})
    dict_field._caster = {'str':'str'}
    dict_field._set_value({'message':'test'})
    with pytest.raises(TypeError):
        dict_field._set_value(1)
    dict_field._caster = {'message':str}
    dict_field._set_value({'message':'test'})
    
    
