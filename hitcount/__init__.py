import django


if django.VERSION < (3, 2):
    default_app_config = "hitcount.apps.HitCountAppConfig"
