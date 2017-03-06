# this function can return json for any etcd key
def read(key):
    result = {}
    job = tendrl_ns.etcd_orm.client.read(key)
    if hasattr(job, 'children'):
        for item in job.leaves:
            if item.dir is True:
                result[item.key.split("/")[-1]] =  read(item.key)
            else:
                result[item.key.split("/")[-1]] = item.value
    return result
