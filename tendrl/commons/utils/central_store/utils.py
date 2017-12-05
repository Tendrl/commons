import datetime
import etcd
import sys
import time
import thread

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
            NS._int.wclient._read = NS._int.wclient.read
            NS._int.wclient.read = read
            NS._int.wclient._write = NS._int.wclient.write
            NS._int.wclient.write = write
            NS._int.wclient._delete = NS._int.wclient.delete
            NS._int.wclient.delete = delete
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
            NS._int.client._read = NS._int.client.read
            NS._int.client.read = read
            NS._int.client._write = NS._int.client.write
            NS._int.client.write = write
            NS._int.client._delete = NS._int.client.delete
            NS._int.client.delete = delete

        except etcd.EtcdException:
            sys.stdout.write(
                "Error connecting to central store (etcd), trying "
                "again...")
            time.sleep(2)


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
