import __future__

import ast
import inspect
import sys
import textwrap
import tokenize

from django.core.exceptions import ImproperlyConfigured

from .env import DeferredEnv
from .options import Options


class SettingsDict(dict):
    def __setitem__(self, key, value):
        if isinstance(value, DeferredEnv):
            try:
                value = value._parse(key)
            except ImproperlyConfigured:
                if value._optional:
                    return
                raise
        super().__setitem__(key, value)


class SettingsMeta(type):
    def __prepare__(name, bases):
        frame = sys._getframe(1)
        filename = inspect.getsourcefile(frame)
        with tokenize.open(filename) as file:
            lines = file.readlines()[frame.f_lineno - 1 :]
        source = "".join(inspect.getblock(lines))
        source = textwrap.dedent(source.expandtabs(tabsize=8))

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
        return SettingsDict(__options__=Options(meta))

    def __new__(meta, name, bases, namespace):
        options = namespace.pop("__options__", None)
        if not isinstance(options, Options):
            raise RuntimeError("__options__ is not an Options object")
        if "Meta" in namespace and not isinstance(namespace["Meta"], type):
            raise TypeError("{}.Meta has to be a class".format(name))
        namespace["_options"] = options
        return super().__new__(meta, name, bases, namespace)

    def __dir__(cls):
        default_settings = cls._options.default_settings
        return set(super().__dir__() + dir(default_settings))

    def __getattr__(cls, name):
        default_settings = cls._options.default_settings
        return getattr(default_settings, name)


class Settings(metaclass=SettingsMeta):
    def __dir__(self):
        default_settings = self._options.default_settings
        return set(super().__dir__() + dir(default_settings))

    def __getattr__(self, name):
        default_settings = self._options.default_settings
        return getattr(default_settings, name)

    def is_overridden(self, setting):
        try:
            self.__getattribute__(setting)  # Avoids __getattr__
        except AttributeError:
            return False
        else:
            return True
