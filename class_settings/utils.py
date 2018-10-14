import functools

from django.conf import settings


def _patch_settings_setup(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        @functools.wraps(settings._setup)
        def _setup(*_args, **_kwargs):
            # Should not get accessed again but might as well clean up after ourselves
            object.__delattr__(settings, "_setup")
            func(*args, **kwargs)

        # Circumvent any custom logic
        object.__setattr__(settings, "_setup", _setup)

    return wrapper
