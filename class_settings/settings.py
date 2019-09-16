import __future__

import ast
import collections
import copy
import inspect
import sys
import textwrap
import tokenize

from django.core.exceptions import ImproperlyConfigured

from .env import DeferredEnv
from .options import Options
from .utils import missing


class SettingsDict(collections.UserDict):
    def __init__(self, *, options, bare_cls):
        super().__init__()
        self.options = options
        self._bare_cls = bare_cls

    def __missing__(self, key):
        if self.options.inject_settings and key.isupper():
            value = getattr(self._bare_cls, key, missing)
            if value is not missing:
                return copy.deepcopy(value)
        raise KeyError(key)

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
    @classmethod
    def __prepare__(meta, name, bases):
        bare_cls = meta("<Bare>", bases, SettingsDict(options=None, bare_cls=None))

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
            meta = getattr(bare_cls, "Meta", None)
        options = Options(meta)
        bare_cls._options = options
        return SettingsDict(options=options, bare_cls=bare_cls)

    def __new__(meta, name, bases, namespace):
        if "Meta" in namespace and not inspect.isclass(namespace["Meta"]):
            raise TypeError("{}.Meta has to be a class".format(name))
        namespace["_options"] = namespace.options
        return super().__new__(meta, name, bases, namespace.data)

    def __dir__(cls):
        default_settings = cls._options.default_settings
        default_dir = [s for s in dir(default_settings) if s.isupper()]
        return {*super().__dir__(), *default_dir}

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
        return {*super().__dir__(), *default_dir}

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
