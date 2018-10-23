import contextlib
import functools
import os

from . import parsers


class Missing:
    def __bool__(self):
        return False


missing = Missing()


class Env:
    def __init__(self):
        self._prefix = None
        self._parsers = {}
        # Populate with default parsers
        for name in dir(parsers):
            parser = getattr(parsers, name)
            if callable(parser):
                self.parser(parser)

    def __call__(self, name=None, *, prefix=None, default=missing):
        if name is None:
            return LazyEnv(prefix, default)
        prefix = prefix if prefix is not None else self._prefix
        name = prefix + name if prefix is not None else name
        if default is not missing:
            return os.environ.get(name, default)
        return os.environ[name]

    def __getattr__(self, name):
        try:
            return self._parsers[name]
        except KeyError:
            raise AttributeError

    @contextlib.contextmanager
    def prefixed(self, prefix):
        old_prefix = self._prefix
        if old_prefix is None:
            self._prefix = prefix
        else:
            self._prefix += prefix
        yield
        self._prefix = old_prefix

    def parser(self, _func=None, *, name=None):
        def decorator(func):
            @functools.wraps(func)
            def parser(name=None, *, prefix=None, default=missing, **kwargs):
                try:
                    value = env(name, prefix=prefix)
                except KeyError:
                    if default is not missing:
                        return default
                    raise
                if isinstance(value, LazyEnv):
                    value.parser = functools.partial(parser, **kwargs)
                else:
                    value = func(value, **kwargs)
                return value

            parser_name = name if name is not None else func.__name__
            self._parsers[parser_name] = parser
            return func

        return decorator if _func is None else decorator(_func)


class LazyEnv:
    def __init__(self, prefix, default=missing):
        self.prefix = prefix
        self.default = default
        self.parser = None

    def __call__(self, name):
        if self.parser is not None:
            return self.parser(name, prefix=self.prefix, default=self.default)
        else:
            return env(name, prefix=self.prefix, default=self.default)


env = Env()
