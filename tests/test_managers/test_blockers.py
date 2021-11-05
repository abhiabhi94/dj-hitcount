from django.test import TestCase

from hitcount.models import BlockedIP
from hitcount.models import BlockedUserAgent


class TestBlockIPManager(TestCase):

    def test_is_blocked(self):
        # without IP.
        self.assertIs(BlockedIP.objects.is_blocked(), False)

        BlockedIP.objects.create(ip='10.1.2.1')

        self.assertIs(BlockedIP.objects.is_blocked('10.1.2.1'), True)
        self.assertIs(BlockedIP.objects.is_blocked('10.1.1.1'), False)


class TestBlockUserAgentManager(TestCase):

    def test_is_blocked(self):
        # without an agent.
        self.assertIs(BlockedUserAgent.objects.is_blocked(), False)

        user_agent_windows = 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
        user_agent_mac = 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:42.0) Gecko/20100101 Firefox/42.0'

        BlockedUserAgent.objects.create(user_agent=user_agent_windows)

        self.assertIs(BlockedUserAgent.objects.is_blocked(user_agent_windows), True)
        self.assertIs(BlockedUserAgent.objects.is_blocked(user_agent_mac), False)
