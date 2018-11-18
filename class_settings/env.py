import contextlib
import functools
import os
import sys
import types

from django.core.exceptions import ImproperlyConfigured

from . import parsers
from .options import Options
from .utils import normalize_prefix


class Missing:
    def __bool__(self):
        return False


missing = Missing()


class Env:
    def __init__(self):
        self._prefix = None
        self._parsers = {}
        # Populate with default parsers
        for name, parser in vars(parsers).items():
            if name.startswith("_"):
                continue
            if callable(parser):
                self.parser(parser)

    def __call__(self, name=None, *, prefix=None, default=missing):
        frame = sys._getframe(1)
        while frame is not None:
            options = frame.f_locals.get("__meta__")
            if isinstance(options, Options):
                break
            frame = frame.f_back
        else:
            if name is None:
                raise TypeError("'name' is required outside of Settings subclasses")
            meta = types.SimpleNamespace(env_prefix=None)
            options = Options(meta)

        if name is None:
            return DeferredEnv(self, prefix=prefix, default=default)
        prefix = normalize_prefix(
            prefix
            if prefix is not None
            else self._prefix
            if self._prefix is not None
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

    @contextlib.contextmanager
    def prefixed(self, prefix):
        prefix = normalize_prefix(prefix)
        old_prefix = self._prefix
        if old_prefix is None:
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
            def parser(name=None, *, prefix=None, default=missing, **kwargs):
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
    def __init__(self, env, *, prefix=None, default=missing):
        self._env = env
        self._prefix = prefix
        self._default = default
        self._parser = None

    def _parse(self, name):
        if self._parser is not None:
            return self._parser(name, prefix=self._prefix, default=self._default)
        else:
            return self._env(name, prefix=self._prefix, default=self._default)


env = Env()
