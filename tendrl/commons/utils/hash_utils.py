import hashlib
import json

def generate_obj_hash(etcd_obj):
    etcd_obj.hash = None
    etcd_obj.updated_at = None
    # Above items cant be part of hash
    _obj_str = "".join(sorted(etcd_obj.json))
    return hashlib.md5(_obj_str).hexdigest()
        
