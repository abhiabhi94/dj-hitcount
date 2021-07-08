from django.test import TestCase

from hitcount.models import BlockedIP
from hitcount.models import BlockedUserAgent


class TestBlockIPManager(TestCase):

    def test_filter_ip(self):
        blocked = BlockedIP.objects.create(ip='10.1.1.1')
        BlockedIP.objects.create(ip='10.1.2.1')

        self.assertQuerysetEqual(BlockedIP.objects.filter_ip(ip='10.1.1.1'), {blocked}, transform=lambda x: x)


class TestBlockUserAgentManager(TestCase):

    def test_filter_user_agent(self):
        user_agent_windows = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
        user_agent_mac = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'

        blocked = BlockedUserAgent.objects.create(user_agent=user_agent_mac)
        BlockedUserAgent.objects.create(user_agent=user_agent_windows)

        self.assertQuerysetEqual(
            BlockedUserAgent.objects.filter_user_agent(user_agent=user_agent_mac),
            {blocked},
            transform=lambda x: x,
        )
