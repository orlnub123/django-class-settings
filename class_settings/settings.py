import importlib
import os

from django.conf import global_settings, settings


class Settings:
    def __getattr__(self, name):
        return getattr(global_settings, name)


def setup():
    module_path = os.environ["DJANGO_SETTINGS_MODULE"]
    cls_path = os.environ["DJANGO_SETTINGS_CLASS"]
    cls = getattr(importlib.import_module(module_path), cls_path)
    settings.configure(cls())
