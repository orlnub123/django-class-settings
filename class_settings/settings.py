import os
import sys

from django.conf import global_settings

from .env import DeferredEnv
from .importers import SettingsImporter


class Options:
    def __init__(self, meta):
        self.default_settings = getattr(meta, "default_settings", global_settings)


class SettingsDict(dict):
    def __setitem__(self, key, value):
        if isinstance(value, DeferredEnv):
            value = value._parse(key)
        super().__setitem__(key, value)


class SettingsMeta(type):
    def __prepare__(name, bases):
        return SettingsDict()

    def __init__(cls, name, bases, namespace):
        meta = getattr(cls, "Meta", None)
        cls._meta = Options(meta)


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
