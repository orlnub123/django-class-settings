import importlib.machinery
import inspect
import os
import pathlib
import time
import types
import warnings

import django
from django.core.exceptions import ImproperlyConfigured
from django.utils.functional import LazyObject

from .settings import Settings
from .utils import missing


class LazySettingsModule(LazyObject):
    def __init__(self):
        super().__init__()
        # Prevent DJANGO_SETTINGS_MODULE getting mutated twice via the autoreloader
        if os.environ.get("RUN_MAIN") != "true":
            try:
                settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
                settings_class = os.environ["DJANGO_SETTINGS_CLASS"]
            except KeyError as exc:
                raise ImproperlyConfigured(
                    "Settings could not be setup. The environment variable "
                    "{!r} is not defined.".format(exc.args[0])
                ) from None
            os.environ["DJANGO_SETTINGS_MODULE"] = "{}:{}".format(
                settings_module, settings_class
            )

    def _setup(self):
        settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
        if SettingsImporter.find_spec(settings_module) is None:
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


class SettingsModule(types.ModuleType):
    def __init__(self, name, settings):
        super().__init__(name, settings.__doc__)
        self.SETTINGS_MODULE = name
        self.SETTINGS_CLASS = settings

    def __dir__(self):
        return {*super().__dir__(), *dir(self.SETTINGS_CLASS)}

    def __getattr__(self, name):
        return getattr(self.SETTINGS_CLASS, name)


class SettingsImporter:
    @classmethod
    def find_spec(cls, fullname, path=None, target=None):
        if ":" not in fullname.rpartition(".")[2]:
            return None
        settings_module = fullname.rsplit(":", maxsplit=1)[0]
        return importlib.machinery.ModuleSpec(fullname, cls, origin=settings_module)

    @classmethod
    def create_module(cls, spec):
        settings_module, settings_class = spec.name.rsplit(":", maxsplit=1)
        module = importlib.import_module(settings_module)
        try:
            settings_cls = getattr(module, settings_class)
        except AttributeError:
            raise ImproperlyConfigured(
                "Module {!r} has no Settings subclass named {!r}".format(
                    settings_module, settings_class
                )
            ) from None
        if not (inspect.isclass(settings_cls) and issubclass(settings_cls, Settings)):
            raise ImproperlyConfigured(
                "{!r} is not a Settings subclass".format(settings_class)
            )
        return SettingsModule(spec.name, settings_cls())

    @classmethod
    def exec_module(cls, module):
        pass
