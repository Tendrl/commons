import datetime

from tendrl.commons.central_store import fields

PY_TO_TENDRL_TYPE_MAP = {dict: fields.DictField,
                         str: fields.StrField,
                         int: fields.IntField,
                         bool: fields.StrField,
                         unicode: fields.StrField,
                         datetime.datetime: fields.DateTimeField,
                         list: fields.ListField}


def to_tendrl_field(name, value):
    return PY_TO_TENDRL_TYPE_MAP[type(value)](name, value)
