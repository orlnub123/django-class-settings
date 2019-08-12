import contextlib
import functools
import os
import sys
import types

from django.core.exceptions import ImproperlyConfigured

from . import parsers
from .options import Options
from .utils import missing


class Env:
    def __init__(self):
        self._prefix = missing
        self._parsers = {}
        # Populate with default parsers
        for name, parser in vars(parsers).items():
            if name.startswith("_"):
                continue
            if callable(parser):
                self.parser(parser)

    def __call__(self, name=None, *, prefix=missing, default=missing, optional=False):
        from .settings import SettingsDict

        frame = sys._getframe(1)
        while frame is not None:
            f_locals = frame.f_locals
            if isinstance(f_locals, SettingsDict):
                options = f_locals.options
                break
            frame = frame.f_back
        else:
            if name is None:
                raise TypeError("'name' is required outside of Settings subclasses")
            if optional:
                raise TypeError(
                    "'optional' is only applicable inside Settings subclasses"
                )
            meta = types.SimpleNamespace(env_prefix=None)
            options = Options(meta)

        if name is None or optional:
            kwargs = {"name": name, "prefix": prefix, "default": default}
            return DeferredEnv(self, kwargs=kwargs, optional=optional)
        prefix = (
            prefix
            if prefix is not missing
            else self._prefix
            if self._prefix is not missing
            else options.env_prefix
        )
        name = prefix + name if prefix is not None else name
        if default is not missing:
            return os.environ.get(name, default)
        try:
            return os.environ[name]
        except KeyError:
            raise ImproperlyConfigured(
                "Environment variable {!r} not set".format(name)
            ) from None

    def __getattr__(self, name):
        try:
            return self._parsers[name]
        except KeyError:
            cls_name = type(self).__name__
            raise AttributeError(
                "{!r} object has no attribute {!r}".format(cls_name, name)
            ) from None

    @staticmethod
    def read_env(file=None):
        from dotenv import load_dotenv

        file = file if file is not None else ".env"
        load_dotenv(file, override=True)

    @contextlib.contextmanager
    def prefixed(self, prefix):
        old_prefix = self._prefix
        if not old_prefix or prefix is None:
            self._prefix = prefix
        else:
            self._prefix += prefix
        try:
            yield
        finally:
            self._prefix = old_prefix

    def parser(self, _func=None, *, name=None, parse_default=False):
        def decorator(func):
            @functools.wraps(func)
            def parser(name=None, *, prefix=missing, default=missing, **kwargs):
                try:
                    value = self(name, prefix=prefix)
                except ImproperlyConfigured:
                    if default is not missing:
                        if parse_default:
                            default = func(default, **kwargs)
                        return default
                    raise
                if isinstance(value, DeferredEnv):
                    value._parser = functools.partial(parser, **kwargs)
                else:
                    value = func(value, **kwargs)
                return value

            parser_name = name if name is not None else func.__name__
            self._parsers[parser_name] = parser
            return func

        return decorator if _func is None else decorator(_func)


class DeferredEnv:
    def __init__(self, env, *, kwargs, optional):
        self._env = env
        self._parser = None
        self._kwargs = kwargs
        self._optional = optional

    def _parse(self, name):
        kwargs = self._kwargs.copy()
        name_kwarg = kwargs.pop("name")
        name = name_kwarg if name_kwarg is not None else name
        if self._parser is not None:
            return self._parser(name, **kwargs)
        else:
            return self._env(name, **kwargs)


env = Env()
