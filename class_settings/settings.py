import __future__

import ast
import inspect
import sys
import textwrap
import tokenize

from .env import DeferredEnv
from .options import Options


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
        source = textwrap.dedent(source.expandtabs())

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
        options = namespace.pop("__meta__", None)
        if not isinstance(options, Options):
            raise RuntimeError("__meta__ is not an Options object")
        if "Meta" in namespace and not isinstance(namespace["Meta"], type):
            raise TypeError("{}.Meta has to be a class".format(name))
        namespace["_meta"] = options
        return super().__new__(meta, name, bases, namespace)


class Settings(metaclass=type("Meta", (type,), {})):  # Hack for __class__ assignment
    def __dir__(self):
        default_settings = self._meta.default_settings
        return set(super().__dir__() + dir(default_settings))

    def __getattr__(self, name):
        default_settings = self._meta.default_settings
        return getattr(default_settings, name)

    def is_overridden(self, setting):
        try:
            self.__getattribute__(setting)  # Avoids __getattr__
        except AttributeError:
            return False
        else:
            return True


Settings.__class__ = SettingsMeta
