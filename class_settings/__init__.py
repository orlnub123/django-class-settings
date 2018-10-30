__version__ = "0.1.0-dev"

from .env import Env, env
from .settings import Settings


def setup():
    import importlib
    import os
    import sys
    from django.conf import settings
    from .importers import SettingsImporter
    from .utils import patch_settings_setup

    global _setup
    if _setup:
        return
    _setup = True

    @patch_settings_setup  # Needed for manage.py --settings support
    def settings_setup():
        module_path = os.environ["DJANGO_SETTINGS_MODULE"]
        module = importlib.import_module(module_path)
        # Allow configure to error on multiple calls
        settings.configure(module, SETTINGS_MODULE=module_path)
        wrapped = settings._wrapped
        settings._setup()
        settings._wrapped = wrapped

    settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
    settings_class = os.environ["DJANGO_SETTINGS_CLASS"]
    os.environ["DJANGO_SETTINGS_MODULE"] = "{}:{}".format(
        settings_module, settings_class
    )
    sys.meta_path.append(SettingsImporter())


_setup = False
