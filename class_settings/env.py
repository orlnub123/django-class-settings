import functools
import os

from . import parsers


class Missing:
    def __bool__(self):
        return False


missing = Missing()


class Env:
    def __init__(self):
        self._parsers = {}
        # Populate with default parsers
        for name in dir(parsers):
            parser = getattr(parsers, name)
            if callable(parser):
                self.parser(parser)

    def __call__(self, name=None, *, prefix=None, default=missing):
        if name is None:
            return LazyEnv(prefix, default)
        env_name = prefix + name if prefix is not None else name
        if default is not missing:
            return os.environ.get(env_name, default)
        return os.environ[env_name]

    def __getattr__(self, name):
        try:
            return self._parsers[name]
        except KeyError:
            raise AttributeError

    def parser(self, _func=None, *, name=None):
        def decorator(func):
            @functools.wraps(func)
            def parser(name=None, *, prefix=None, default=missing, **kwargs):
                value = env(name, prefix=prefix, default=default)
                if isinstance(value, LazyEnv):
                    value.parser = functools.partial(func, **kwargs)
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
        value = env(name, prefix=self.prefix, default=self.default)
        return self.parser(value) if self.parser is not None else value


env = Env()
