import functools

from django.conf import settings


def patch_settings_setup(func):
    @functools.wraps(settings._setup)
    def setup(*args, **kwargs):
        object.__delattr__(settings, "_setup")
        func()

    # Circumvent any custom logic
    object.__setattr__(settings, "_setup", setup)
    return func


def normalize_prefix(prefix):
    if prefix.islower():
        if not prefix.endswith("_"):
            prefix += "_"
        prefix = prefix.upper()
    return prefix
