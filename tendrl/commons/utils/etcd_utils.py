import etcd

'''
   Read from etcd
   input params:
       key  : type  - >  string
              value - >  attr to be fetched

   return param:
       dict - > if read is successful
       None - > if key is not found
'''


def read(key, **kwargs):
    try:
        return NS._int.client.read(key, **kwargs)
    except (etcd.EtcdConnectionFailed, etcd.EtcdException) as ex:
        if type(ex) in [etcd.EtcdKeyNotFound,
                        etcd.EtcdCompareFailed,
                        etcd.EtcdAlreadyExist
                       ]:
            raise ex
        else:
            NS._int.reconnect()
            return NS._int.client.read(key, **kwargs)


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


def write(key, value, quorum=True, **kwargs):
    try:
        return NS._int.wclient.write(key, value, quorum=quorum,
                                     **kwargs)
    except (etcd.EtcdConnectionFailed, etcd.EtcdException) as ex:
        if type(ex) in [etcd.EtcdKeyNotFound,
                        etcd.EtcdCompareFailed,
                        etcd.EtcdAlreadyExist]:
            raise ex
        else:
            NS._int.wreconnect()
            return NS._int.wclient.write(key, value,
                                         quorum=quorum,
                                         **kwargs
                                        )

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


def refresh(value, ttl, **kwargs):
    try:
        NS._int.wclient.refresh(value, ttl=ttl,
                                **kwargs)
    except (etcd.EtcdConnectionFailed, etcd.EtcdException) as ex:
        if type(ex) in [etcd.EtcdKeyNotFound,
                        etcd.EtcdCompareFailed,
                        etcd.EtcdAlreadyExist]:
            raise ex
        else:
            NS._int.wreconnect()
            NS._int.wclient.refresh(value, ttl=ttl,
                                    **kwargs)


'''
   Delete from etcd
   input params:
       key  : type  - >  string
              value - >  attr to be deleted

   return param:
       None - > if delete is successful
       None - > if key is not found
'''


def delete(key, **kwargs):
    try:
        return NS._int.wclient.delete(key, **kwargs)
    except (etcd.EtcdConnectionFailed, etcd.EtcdException) as ex:
        if type(ex) in [etcd.EtcdKeyNotFound,
                        etcd.EtcdCompareFailed,
                        etcd.EtcdAlreadyExist]:
            raise ex
        else:
            NS._int.wreconnect()
            return NS._int.wclient.delete(key, **kwargs)
