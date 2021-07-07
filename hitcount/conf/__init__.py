import django
from django.conf import settings as django_settings
from django.utils.functional import LazyObject

from hitcount.conf import defaults as app_settings


class LazySettings(LazyObject):
    def _setup(self):
        self._wrapped = Settings(app_settings, django_settings)


_DEPRECATED_DJANGO_SETTINGS = {
    'USE_TZ' if django.VERSION > (4, 0) else None,
    'PASSWORD_RESET_TIMEOUT_DAYS' if django.VERSION > (3, 0) else None,
    'DEFAULT_CONTENT_TYPE' if django.VERSION > (2, 2) else None,
    'FILE_CHARSET' if django.VERSION > (2, 2) else None,
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
