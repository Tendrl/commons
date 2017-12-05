import datetime
import etcd
import sys
import time

from tendrl.commons.utils.central_store import fields

PY_TO_TENDRL_TYPE_MAP = {dict: fields.DictField,
                         str: fields.StrField,
                         int: fields.IntField,
                         bool: fields.StrField,
                         unicode: fields.StrField,
                         datetime.datetime: fields.DateTimeField,
                         list: fields.ListField}


def to_tendrl_field(name, value, tendrl_type=None):
    if tendrl_type:
        if tendrl_type in ['json' or 'list']:
            return PY_TO_TENDRL_TYPE_MAP[str](name, value)

    return PY_TO_TENDRL_TYPE_MAP[type(value)](name, value)


def wreconnect():
    NS._int.wclient = None
    while not NS._int.wclient:
        try:
            NS._int.wclient = etcd.Client(**NS._int.etcd_kwargs)
        except etcd.EtcdException:
            sys.stdout.write(
                "Error connecting to central store (etcd), trying "
                "again...")
            time.sleep(2)


def reconnect():
    NS._int.client = None
    while not NS._int.client:
        try:
            NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
        except etcd.EtcdException:
            sys.stdout.write(
                "Error connecting to central store (etcd), trying "
                "again...")
            time.sleep(2)


def read(*args, **kws):
    _success = False
    while not _success:
        try:
            _res = NS._int.client._read(*args, **kws)
            _sucess = True
            return _res
        except etcd.EtcdConnectionFailed:
            reconnect()

def write(*args, **kws):
    _success = False
    while not _success:
        try:
            _res = NS._int.wclient._write(*args, **kws)
            _sucess = True
            return _res
        except etcd.EtcdConnectionFailed:
            wreconnect()

def delete(*args, **kws):
    _success = False
    while not _success:
        try:
            _res = NS._int.wclient._delete(*args, **kws)
            _sucess = True
            return _res
        except etcd.EtcdConnectionFailed:
            wreconnect()
