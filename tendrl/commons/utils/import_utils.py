# coding=utf-8
import importlib
import inspect

def load_abs_module(module_abs_path):
    return importlib.import_module(module_abs_path)


def load_abs_class(class_abs_path):
    kls_name = class_abs_path.split(".")[-1]
    module_name = ".".join(class_abs_path.split(".")[:-1])
    module = load_abs_module(module_name)
    obj = inspect.getmembers(module, inspect.isclass)
    for cls_name,cls_type in obj:
        if kls_name in cls_name:
            return cls_type
    return None
