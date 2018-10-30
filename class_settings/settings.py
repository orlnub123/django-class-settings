import __future__

import ast
import inspect
import os
import sys
import tokenize

from django.conf import global_settings

from .env import DeferredEnv
from .importers import SettingsImporter


class Options:
    def __init__(self, meta):
        self.default_settings = getattr(meta, "default_settings", global_settings)
        self.env_prefix = getattr(meta, "env_prefix", "DJANGO_")


class SettingsDict(dict):
    def __setitem__(self, key, value):
        if isinstance(value, DeferredEnv):
            value = value._parse(key)
        super().__setitem__(key, value)


class SettingsMeta(type):
    def __prepare__(name, bases):
        frame = sys._getframe(1)
        filename = inspect.getsourcefile(frame)
        with tokenize.open(filename) as file:
            lines = file.readlines()[frame.f_lineno - 1 :]
        source = "".join(inspect.getblock(lines))

        cls_node = ast.parse(source).body[0]
        for node in reversed(list(ast.iter_child_nodes(cls_node))):
            if isinstance(node, ast.ClassDef) and node.name == "Meta":
                cf_mask = sum(
                    getattr(__future__, feature).compiler_flag
                    for feature in __future__.all_feature_names
                )
                code = compile(
                    ast.Module(body=[node]),
                    filename="<meta>",
                    mode="exec",
                    flags=frame.f_code.co_flags & cf_mask,
                    dont_inherit=True,
                )
                globals = frame.f_globals
                locals = {}
                exec(code, globals, locals)
                meta = locals["Meta"]
                break
        else:
            for base in bases:
                if hasattr(base, "Meta"):
                    meta = base.Meta
                    break
            else:
                meta = None
        return SettingsDict(__meta__=Options(meta))

    def __new__(meta, name, bases, namespace):
        options = namespace.pop("__meta__")
        namespace["_meta"] = options
        return super().__new__(meta, name, bases, namespace)


class Settings(metaclass=type("Meta", (type,), {})):  # Hack for __class__ assignment
    def __getattr__(self, name):
        default_settings = self._meta.default_settings
        return getattr(default_settings, name)


Settings.__class__ = SettingsMeta


def setup():
    settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
    settings_class = os.environ["DJANGO_SETTINGS_CLASS"]
    os.environ["DJANGO_SETTINGS_MODULE"] = "{}:{}".format(
        settings_module, settings_class
    )
    sys.meta_path.append(SettingsImporter())
