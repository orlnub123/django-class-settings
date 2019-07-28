import __future__

import ast
import copy
import importlib
import inspect
import os
import pathlib
import sys
import textwrap
import time
import tokenize
import warnings

import django
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import LazyObject

from .env import DeferredEnv
from .options import Options
from .utils import missing


class LazySettings(LazyObject):
    def __init__(self):
        super().__init__()
        # Prevent DJANGO_SETTINGS_MODULE getting mutated twice via the autoreloader
        if os.environ.get("RUN_MAIN") != "true":
            try:
                settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
                settings_class = os.environ["DJANGO_SETTINGS_CLASS"]
            except KeyError as error:
                raise ImproperlyConfigured(
                    "Settings could not be setup. The environment variable "
                    "{!r} is not defined.".format(error.args[0])
                ) from None
            os.environ["DJANGO_SETTINGS_MODULE"] = "{}:{}".format(
                settings_module, settings_class
            )

    def _setup(self):
        from .importers import SettingsImporter

        settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
        if SettingsImporter().find_spec(settings_module) is None:
            raise ImproperlyConfigured(
                "The settings module {!r} is not formatted as "
                "'{{module}}:{{class}}'".format(settings_module)
            )
        module = importlib.import_module(settings_module)
        # Keep updated against django.conf.Settings.__init__
        self.check_tuple_settings(module)
        self.check_secret_key(module)
        self.check_default_content_type(module)
        self.check_file_charset(module)
        self.check_time_zone(module)
        self._wrapped = module

    def check_tuple_settings(self, module):
        for setting in ("INSTALLED_APPS", "TEMPLATE_DIRS", "LOCALE_PATHS"):
            value = getattr(module, setting, missing)
            if value is not missing and not isinstance(value, (list, tuple)):
                raise ImproperlyConfigured(
                    "The {} setting must be a list or a tuple.".format(setting)
                )

    def check_secret_key(self, module):
        if not getattr(module, "SECRET_KEY", False):
            raise ImproperlyConfigured("The SECRET_KEY setting must not be empty.")

    def check_default_content_type(self, module):
        if not (2, 0) <= django.VERSION[:2] < (3, 0):
            return

        from django.utils.deprecation import RemovedInDjango30Warning

        if module.is_overridden("DEFAULT_CONTENT_TYPE"):
            warnings.warn(
                "The DEFAULT_CONTENT_TYPE setting is deprecated.",
                RemovedInDjango30Warning,
            )

    def check_file_charset(self, module):
        if not (2, 2) <= django.VERSION[:2] < (3, 1):
            return

        from django.utils.deprecation import RemovedInDjango31Warning

        if module.is_overridden("FILE_CHARSET"):
            warnings.warn(
                "The FILE_CHARSET setting is deprecated. Starting with Django "
                "3.1, all files read from disk must be UTF-8 encoded.",
                RemovedInDjango31Warning,
            )

    def check_time_zone(self, module):
        time_zone = getattr(module, "TIME_ZONE", False)
        if time_zone and hasattr(time, "tzset"):
            zoneinfo_root = pathlib.Path("/usr/share/zoneinfo")
            zoneinfo_file = zoneinfo_root.joinpath(*time_zone.split("/"))
            if zoneinfo_root.exists() and not zoneinfo_file.exists():
                raise ValueError("Incorrect timezone setting: {}".format(time_zone))
            os.environ["TZ"] = time_zone
            time.tzset()


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
