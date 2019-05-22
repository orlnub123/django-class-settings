import __future__

import ast
import copy
import inspect
import sys
import textwrap
import tokenize

from django.core.exceptions import ImproperlyConfigured

from .env import DeferredEnv
from .options import Options


class SettingsDict(dict):
    def __init__(self, *, options, bases):
        super().__init__(__options__=options)
        if options.inject_settings:
            to_inject = {}
            for base in reversed(bases):
                for setting in dir(base):
                    if not setting.isupper():
                        continue
                    value = getattr(base, setting)
                    to_inject[setting] = copy.deepcopy(value)
            self.update(to_inject)

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
                    ast.Module(body=[node], type_ignores=[]),
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
        return SettingsDict(options=Options(meta), bases=bases)

    def __new__(meta, name, bases, namespace):
        options = namespace.pop("__options__", None)
        if not isinstance(options, Options):
            raise AttributeError("__options__ cannot be overwritten")
        if "Meta" in namespace and not isinstance(namespace["Meta"], type):
            raise TypeError("{}.Meta has to be a class".format(name))
        namespace["_options"] = options
        return super().__new__(meta, name, bases, namespace)

    def __dir__(cls):
        default_settings = cls._options.default_settings
        default_dir = [s for s in dir(default_settings) if s.isupper()]
        return set(super().__dir__() + default_dir)

    def __getattr__(cls, name):
        if not name.isupper():
            raise AttributeError(
                "type object {!r} has no attribute {!r}".format(cls.__name__, name)
            )
        default_settings = cls._options.default_settings
        return getattr(default_settings, name)


class Settings(metaclass=SettingsMeta):
    def __dir__(self):
        default_settings = self._options.default_settings
        default_dir = [s for s in dir(default_settings) if s.isupper()]
        return set(super().__dir__() + default_dir)

    def __getattr__(self, name):
        if not name.isupper():
            raise AttributeError(
                "{!r} object has no attribute {!r}".format(type(self).__name__, name)
            )
        default_settings = self._options.default_settings
        return getattr(default_settings, name)

    def is_overridden(self, setting):
        try:
            self.__getattribute__(setting)  # Avoids __getattr__
        except AttributeError:
            return False
        else:
            return True
