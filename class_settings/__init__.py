__all__ = ["Env", "Settings", "env", "setup"]
__version__ = "0.2.0-dev"

from .env import Env, env
from .settings import Settings


def setup():
    import os
    import sys
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    from django.utils.functional import SimpleLazyObject
    from .importers import SettingsImporter
    from .settings import LazySettings

    global _setup
    if _setup:
        return

    # Prevent DJANGO_SETTINGS_MODULE getting mutated twice via the autoreloader
    if os.environ.get("RUN_MAIN") != "true":
        try:
            settings_module = os.environ["DJANGO_SETTINGS_MODULE"]
            settings_class = os.environ["DJANGO_SETTINGS_CLASS"]
        except KeyError as error:
            raise ImproperlyConfigured(
                "Settings could not be setup. The environment variable {!r} "
                "is not defined.".format(error.args[0])
            ) from None
        os.environ["DJANGO_SETTINGS_MODULE"] = "{}:{}".format(
            settings_module, settings_class
        )
    sys.meta_path.append(SettingsImporter())
    default_settings = LazySettings()
    settings_module = SimpleLazyObject(lambda: default_settings.SETTINGS_MODULE)
    settings.configure(default_settings, SETTINGS_MODULE=settings_module)

    _setup = True


_setup = False
