import datetime
import json

from tendrl.commons.etcdobj import fields


def to_etcdobj(cls_etcd, obj):
    for attr, value in vars(obj).iteritems():
        if value is None:
            value = ""
        if attr.startswith("_") or attr in ['value', 'list']:
            continue
        if type(value) == list:
            value = json.dumps(value)
        setattr(cls_etcd, attr, to_etcd_field(attr, value))
    return cls_etcd


def to_etcd_field(name, value):
    type_to_etcd_fields_map = {dict: fields.DictField,
                               str: fields.StrField,
                               int: fields.IntField,
                               bool: fields.StrField,
                               unicode: fields.StrField,
                               datetime.datetime: fields.StrField}
    if type(value) == dict:
        return fields.DictField(name, value, {'str': 'str'})
    return type_to_etcd_fields_map[type(value)](name, value)
