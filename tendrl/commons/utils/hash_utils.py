import hashlib
import json

def generate_obj_hash(etcd_obj):
    _obj = json.loads(etcd_obj.json)
    _obj.pop("hash", None)
    _obj.pop("updated_at", None)
    _obj_str = "".join(sorted(json.dumps(_obj)))
    return hashlib.md5(_obj_str).hexdigest()
        
