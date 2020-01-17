from django.conf import global_settings


class Options:
    defaults = {
        "default_settings": global_settings,
        "inject_settings": False,
        "env_prefix": "DJANGO_",
    }

    def __init__(self, meta):
        for option, default in self.defaults.items():
            setattr(self, option, getattr(meta, option, default))
