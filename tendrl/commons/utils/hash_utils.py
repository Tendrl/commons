import hashlib

def generate_obj_hash(etcd_obj):
    _obj_str = ""
    for item in etcd_obj.render():
        if item['name'] in ['value', 'list', 'updated_at', 'hash']:
            continue
        _obj_str += item['value']
    _obj_str = "".join(sorted(_obj_str))
    return hashlib.md5(_obj_str).hexdigest()
        
