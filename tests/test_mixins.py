from datetime import timedelta
from importlib import import_module
from unittest.mock import patch

from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone

from hitcount.conf import settings
from hitcount.mixins import HitCountViewMixin
from hitcount.models import BlockedIP
from hitcount.models import BlockedUserAgent
from hitcount.models import Hit
from hitcount.models import HitCount
from tests.test_views import BaseHitCountViewTest


@patch.object(settings, "HITCOUNT_USE_IP", True)
class TestHitCountViewMixin(BaseHitCountViewTest):
    def test_when_use_ip_is_disabled(self):
        with patch.object(settings, "HITCOUNT_USE_IP", False):
            response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: session key")

        # test database
        hit = Hit.objects.last()
        self.assertIsNone(hit.ip)

    def test_session_key_is_not_present(self):
        session = SessionStore(session_key=None)

        self.request_post.session = session

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: session key")
        # test database
        hit = Hit.objects.last()
        self.assertIsNotNone(hit.session)

    def test_anonymous_user_hit(self):
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: session key")

    @patch.object(settings, "HITCOUNT_HITS_PER_SESSION_LIMIT", 1)
    def test_multiple_anonymous_user_hit_not_counted_with_session_limit(self):
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: session key")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, "Not counted: hits per session limit reached.")

    def test_multiple_anonymous_user_hit_counted_after_filter_active(self):
        # create a Hit ten days ago
        created = timezone.now() - timedelta(days=10)
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = created

            response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: session key")

        # test a Hit today, within the filter time
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: session key")

    def test_registered_user_hit(self):
        self.request_post.user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: user authentication")

    @patch.object(settings, "HITCOUNT_HITS_PER_SESSION_LIMIT", 1)
    def test_registered_user_hit_with_session_limit(self):
        self.request_post.user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: user authentication")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, "Not counted: hits per session limit reached.")

    def test_registered_user_hit_counted_after_filter_active(self):
        self.request_post.user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")

        # create a Hit ten days ago
        created = timezone.now() - timedelta(days=10)
        with patch("django.utils.timezone.now") as mock_now:
            mock_now.return_value = created

            response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: user authentication")

        # test a Hit today, within the filter time
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: user authentication")

    def test_hits_per_ip_limit(self):
        """
        Test `HITCOUNT_HITS_PER_IP_LIMIT` setting.  Should allow multiple hits
        from the same IP until the limit is reached from that IP.
        """
        with patch.object(settings, "HITCOUNT_HITS_PER_IP_LIMIT", 2):
            responses = []
            for _ in range(3):
                # need a new session key each time.
                engine = import_module(settings.SESSION_ENGINE)
                store = engine.SessionStore()
                store.save()
                self.request_post.session = store
                responses.append(HitCountViewMixin.hit_count(self.request_post, self.hit_count))

        self.assertIs(responses[0].hit_counted, True)
        self.assertEqual(responses[0].hit_message, "Hit counted: session key")
        self.assertIs(responses[1].hit_counted, True)
        self.assertEqual(responses[1].hit_message, "Hit counted: session key")
        self.assertIs(responses[2].hit_counted, False)
        self.assertEqual(responses[2].hit_message, "Not counted: hits per IP address limit reached")
        # test database changes
        hit_count = HitCount.objects.get(pk=self.hit_count.pk)

        self.assertEqual(hit_count.hits, 2)

    @patch.object(settings, "HITCOUNT_HITS_PER_SESSION_LIMIT", 1)
    def test_hits_per_session_limit_for_anonymous_user(self):
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: session key")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, "Not counted: hits per session limit reached.")

    @patch.object(settings, "HITCOUNT_HITS_PER_SESSION_LIMIT", 1)
    def test_hits_per_session_limit_for_authenticated_user(self):
        self.request_post.user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: user authentication")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, "Not counted: hits per session limit reached.")

    @patch.object(settings, "HITCOUNT_EXCLUDE_USER_GROUP", ("Admin",))
    def test_excluded_user_group_not_counted(self):
        self.request_post.user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")
        group = Group.objects.create(name="Admin")
        group.user_set.add(self.request_post.user)

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, "Not counted: user group has been excluded")

    @patch.object(settings, "HITCOUNT_EXCLUDE_USER_GROUP", ("Admin",))
    def test_not_excluded_user_group_counted(self):
        self.request_post.user = User.objects.create_user("john", "lennon@thebeatles.com", "johnpassword")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, "Hit counted: user authentication")

    def test_blocked_ip(self):
        BlockedIP.objects.create(ip="127.0.0.1")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, "Not counted: user IP has been blocked")

    def test_blocked_user_agent(self):
        BlockedUserAgent.objects.create(user_agent="my_clever_agent")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, "Not counted: user agent has been blocked")
