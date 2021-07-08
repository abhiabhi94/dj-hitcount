from django.db import models


class BlockedIPManager(models.Manager):
    def filter_ip(self, ip):
        return self.filter(ip__exact=ip)


class BlockedUserAgentManager(models.Manager):
    def filter_user_agent(self, user_agent):
        return self.filter(user_agent__exact=user_agent)
