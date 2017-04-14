import hashlib

def generate_obj_hash(etcd_obj):
    _obj_str = "".join(sorted(etcd_obj.json))
    return hashlib.md5(_obj_str).hexdigest()
        
