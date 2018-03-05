# flake8:noqa
import datetime
import etcd
import sys
import thread
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
    sys.stderr.write("Error connecting to central store (etcd), trying "
                     "again...")
    time.sleep(2)
    NS._int.wclient = None
    NS._int.wclient = etcd.Client(**NS._int.etcd_kwargs)
    NS._int.wclient._read = NS._int.wclient.read
    NS._int.wclient.read = read
    NS._int.wclient._write = NS._int.wclient.write
    NS._int.wclient.write = write
    NS._int.wclient._delete = NS._int.wclient.delete
    NS._int.wclient.delete = delete


def reconnect():
    sys.stderr.write("Error connecting to central store (etcd), trying "
                     "again...")
    time.sleep(2)
    NS._int.client = None
    NS._int.client = etcd.Client(**NS._int.etcd_kwargs)
    NS._int.client._read = NS._int.client.read
    NS._int.client.read = read
    NS._int.client._write = NS._int.client.write
    NS._int.client.write = write
    NS._int.client._delete = NS._int.client.delete
    NS._int.client.delete = delete


def read(*args, **kws):
    _tries = 0
    while _tries < 5:
        try:
            return NS._int.client._read(*args, **kws)
        except etcd.EtcdConnectionFailed:
            _tries += 1
            reconnect()

    thread.interrupt_main()


def write(*args, **kws):
    _tries = 0
    while _tries < 5:
        try:
            return NS._int.wclient._write(*args, **kws)
        except etcd.EtcdConnectionFailed:
            _tries += 1
            wreconnect()

    thread.interrupt_main()


def delete(*args, **kws):
    _tries = 0
    while _tries < 5:
        try:
            return NS._int.wclient._delete(*args, **kws)
        except etcd.EtcdConnectionFailed:
            _tries += 1
            wreconnect()

    thread.interrupt_main()


def watch(obj, key):

    while True:
        try:
            for change in NS._int.client.eternal_watch(key):
                is_deleted = change._prev_node.value is None and \
                             change.value is None
                if change._prev_node.value != change.value or is_deleted:
                    attr = key.rstrip("/").split("/")[-1]
                    obj.on_change(attr, change._prev_node.value,
                                  change.value)
        except etcd.EtcdKeyNotFound:
            NS._int.watchers.pop(key, None)
            return

