from django.conf import global_settings


class Options:
    def __init__(self, meta):
        self.default_settings = getattr(meta, "default_settings", global_settings)
        self.env_prefix = getattr(meta, "env_prefix", "DJANGO_")
