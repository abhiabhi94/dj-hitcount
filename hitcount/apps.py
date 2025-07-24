from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class HitCountAppConfig(AppConfig):
    name = "hitcount"
    verbose_name = _("hitcount")

    def ready(self):
        import hitcount.signals  # noqa: F401
