# coding=utf-8
import importlib


def load_abs_module(module_abs_path):
    return importlib.import_module(module_abs_path)


def load_abs_class(class_abs_path):
    kls_name = class_abs_path.split(".")[:-1]
    module_name = ".".join(class_abs_path.split(".")[:-1])
    return getattr(kls_name, load_abs_module(module_name))
