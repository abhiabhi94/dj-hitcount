from django.db import models
from django.utils.translation import gettext_lazy as _

from hitcount.managers import BlockedIPManager
from hitcount.managers import BlockedUserAgentManager


class BlockedIP(models.Model):
    ip = models.CharField(max_length=40, unique=True)
    objects = BlockedIPManager()

    class Meta:
        verbose_name = _("Blocked IP")
        verbose_name_plural = _("Blocked IPs")

    def __str__(self):
        return self.ip


class BlockedUserAgent(models.Model):
    user_agent = models.CharField(max_length=255, unique=True)
    objects = BlockedUserAgentManager()

    class Meta:
        verbose_name = _("Blocked User Agent")
        verbose_name_plural = _("Blocked User Agents")

    def __str__(self):
        return "%s" % self.user_agent
