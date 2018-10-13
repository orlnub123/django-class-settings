import importlib
import os

from django.conf import global_settings, settings


class Options:
    def __init__(self, meta):
        self.default_settings = getattr(meta, "default_settings", global_settings)


class SettingsMeta(type):
    def __init__(cls, name, bases, namespace):
        meta = getattr(cls, "Meta", None)
        cls._meta = Options(meta)


class Settings(metaclass=type("Meta", (type,), {})):  # Hack for __class__ assignment
    def __getattr__(self, name):
        default_settings = self._meta.default_settings
        return getattr(default_settings, name)


Settings.__class__ = SettingsMeta


def setup():
    module_path = os.environ["DJANGO_SETTINGS_MODULE"]
    cls_path = os.environ["DJANGO_SETTINGS_CLASS"]
    cls = getattr(importlib.import_module(module_path), cls_path)
    settings.configure(cls())
