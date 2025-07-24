from django.test import SimpleTestCase

from hitcount.models import BlockedIP
from hitcount.models import BlockedUserAgent


class TestBlockedUserAgent(SimpleTestCase):
    def test_string_representation(self):
        ua_text = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4)"

        ua = BlockedUserAgent(user_agent=ua_text)

        self.assertEqual(str(ua), ua_text)


class TestBlockedIPModel(SimpleTestCase):
    def test_string_representation(self):
        ip = BlockedIP(ip="127.0.0.1")

        self.assertEqual(str(ip), "127.0.0.1")
