import django
from django.conf import settings as django_settings
from django.utils.functional import LazyObject

from hitcount.conf import defaults as app_settings


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings(app_settings, django_settings)


_django_version = django.VERSION

_DEPRECATED_DJANGO_SETTINGS = {
    "DEFAULT_FILE_STORAGE" if (4, 2) <= _django_version < (5, 1) else None,
    "STATICFILES_STORAGE" if (4, 2) <= _django_version < (5, 1) else None,
    "USE_L10N" if (4, 0) <= _django_version < (5, 0) else None,
}


class Settings:
    def __init__(self, *args):
        [
            setattr(self, attr, getattr(item, attr))
            for item in args
            for attr in dir(item)
            if attr == attr.upper() and attr.upper() not in _DEPRECATED_DJANGO_SETTINGS
        ]


settings = LazySettings()
