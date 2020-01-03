__all__ = ["Env", "Settings", "env", "setup"]
__version__ = "0.2.0"

from .env import Env, env
from .settings import Settings


def setup():
    import sys
    from django.conf import settings
    from django.utils.functional import SimpleLazyObject
    from .importers import SettingsImporter, LazySettingsModule

    global _setup
    if _setup:
        return

    sys.meta_path.append(SettingsImporter)
    default_settings = LazySettingsModule()
    settings_module = SimpleLazyObject(lambda: default_settings.SETTINGS_MODULE)
    settings.configure(default_settings, SETTINGS_MODULE=settings_module)

    _setup = True


_setup = False
