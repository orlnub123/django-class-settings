__version__ = "0.1.0-dev"

from .env import Env, env
from .settings import Settings


def setup():
    import os
    import sys
    from .importers import SettingsImporter

    settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
    settings_class = os.environ["DJANGO_SETTINGS_CLASS"]
    os.environ["DJANGO_SETTINGS_MODULE"] = "{}:{}".format(
        settings_module, settings_class
    )
    sys.meta_path.append(SettingsImporter())
