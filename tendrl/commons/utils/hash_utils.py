import hashlib
import json

def generate_obj_hash(etcd_obj):
    if hasattr(etcd_obj, "hash"):
        del etcd_obj.hash
    if hasattr(etcd_obj, "updated_at"):
        del etcd_obj.updated_at
    _obj_str = "".join(sorted(etcd_obj.json))
    return hashlib.md5(_obj_str).hexdigest()
        
