import etcd
import __builtin__

'''
   Read from etcd
   input params:
       key  : type  - >  string
              value - >  attr to be fetched

   return param:
       dict - > if read is successful
       None - > if key is not found
'''
 
def read(key):
    try:
        return NS._int.client.read(key)
    except (etcd.EtcdConnectionFailed, etcd.EtcdException) as ex:
        if type(ex) != etcd.EtcdKeyNotFound:
            NS._int.reconnect()
            return NS._int.client.read(key)
        else:
            raise etcd.EtcdKeyNotFound


'''
   Write to etcd
   input params:
       key   : type  - >  string
               value - >  attr to be inserted
       value : type  - >  string/int etc
               value - >  value of attr to be inserted
       quorum: type  - >  bool
               value - >  value for quorum (True/False)
                          default : True

   return param:
       None
'''

def write(key,value,quorum = True):
    try:
        NS._int.wclient.write(key,value,quorum = quorum)
    except (etcd.EtcdConnectionFailed, etcd.EtcdException) as ex:
        if type(ex) != etcd.EtcdKeyNotFound:
            NS._int.wreconnect()
            NS._int.wclient.write(key,value,quorum = quorum)


'''
   Refresh connection
   input params:
       value: type  - >  string
              value - >  etcd path
       ttl  : type - >  int
              value - >  ttl value

   return param:
       None
'''

def refresh(value,ttl):
    try:
        NS._int.wclient.refresh(value, ttl=ttl)
    except (etcd.EtcdConnectionFailed, etcd.EtcdException) as ex:
        if type(ex) != etcd.EtcdKeyNotFound:
            NS._int.wreconnect()
            NS._int.wclient.refresh(value, ttl=ttl)
