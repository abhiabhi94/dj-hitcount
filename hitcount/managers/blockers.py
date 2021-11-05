from django.db import models


class BlockedIPManager(models.Manager):
    def is_blocked(self, ip=None):
        if not ip:
            return False
        return self.filter(ip__exact=ip).exists()


class BlockedUserAgentManager(models.Manager):
    def is_blocked(self, user_agent=None):
        if not user_agent:
            return False

        return self.filter(user_agent__exact=user_agent).exists()
