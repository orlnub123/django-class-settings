__version__ = "0.1.3"

from .env import Env, env
from .settings import Settings


def setup():
    import importlib
    import os
    import sys
    from django.conf import settings
    from django.core.exceptions import ImproperlyConfigured
    from .importers import SettingsImporter
    from .utils import patch_settings_setup

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

    @patch_settings_setup  # Needed for manage.py --settings support
    def settings_setup():
        module_path = os.environ["DJANGO_SETTINGS_MODULE"]
        module = importlib.import_module(module_path)
        # Prevent manage.py from swallowing exceptions arising from
        # settings._setup and make sure to call settings.configure first to
        # allow it to error on multiple calls.
        old = settings._wrapped
        settings.configure(module, SETTINGS_MODULE=module_path)
        new = settings._wrapped
        settings._wrapped = old
        settings._setup()
        settings._wrapped = new

    _setup = True


_setup = False
