import importlib.machinery
import types

from django.core.exceptions import ImproperlyConfigured


class SettingsModule(types.ModuleType):
    def __init__(self, name, cls):
        super().__init__(name, cls.__doc__)
        self.SETTINGS_CLASS = cls

    def __dir__(self):
        return set(super().__dir__() + dir(self.SETTINGS_CLASS))

    def __getattr__(self, name):
        return getattr(self.SETTINGS_CLASS, name)


class SettingsImporter:
    def find_spec(self, fullname, path=None, target=None):
        if ":" not in fullname.rpartition(".")[2]:
            return None
        settings_module = fullname.rsplit(":", maxsplit=1)[0]
        return importlib.machinery.ModuleSpec(fullname, self, origin=settings_module)

    def create_module(self, spec):
        settings_module, settings_class = spec.name.rsplit(":", maxsplit=1)
        module = importlib.import_module(settings_module)
        # manage.py only catches ImproperlyConfigured and ImportError
        try:
            cls = getattr(module, settings_class)
        except AttributeError as error:
            raise ImproperlyConfigured(error)
        return SettingsModule(spec.name, cls())

    def exec_module(self, module):
        pass
