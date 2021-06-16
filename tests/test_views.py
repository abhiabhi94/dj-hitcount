import json
from datetime import timedelta
from importlib import import_module
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import Group
from django.contrib.auth.models import User
from django.http import Http404
from django.test import RequestFactory
from django.test import TestCase
from django.utils import timezone

from blog.models import Post
from hitcount.conf import settings
from hitcount.mixins import HitCountViewMixin
from hitcount.models import BlockedIP
from hitcount.models import BlockedUserAgent
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountDetailView
from hitcount.views import HitCountJSONView

HitCount = get_hitcount_model()


class HitCountTestBase(TestCase):

    def setUp(self):
        self.post = Post.objects.create(title='my title', content='my text')
        self.hit_count = HitCount.objects.create(content_object=self.post)
        self.factory = RequestFactory()
        self.request_post = self.factory.post(
            '/',
            {'hitcountPK': self.hit_count.pk},
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT='my_clever_agent',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.request_get = self.factory.get(
            '/',
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT='my_clever_agent',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')

        self.engine = import_module(settings.SESSION_ENGINE)
        self.store = self.engine.SessionStore()
        self.store.save()
        self.request_post.session = self.store
        self.request_post.user = AnonymousUser()
        self.request_get.session = self.store
        self.request_get.user = AnonymousUser()


class UpdateHitCountTests(HitCountTestBase):

    def test_anonymous_user_hit(self):
        """
        Test AnonymousUser Hit
        """
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, 'Hit counted: session key')

    def test_anonymous_user_hit_not_counted(self):
        """
        Test Multiple AnonymousUser Hit, not counted
        """

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, 'Hit counted: session key')

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, 'Not counted: session key has active hit')

    def test_anonymous_user_hit_counted_after_filter_active(self):
        """
        Test Multiple AnonymousUser Hit, counted because of filter active
        """
        # create a Hit ten days ago
        created = timezone.now() - timedelta(days=10)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = created

            response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, 'Hit counted: session key')

        # test a Hit today, within the filter time
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, 'Hit counted: session key')

    def test_registered_user_hit(self):
        """
        Test AnonymousUser Hit
        """
        self.request_post.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, 'Hit counted: user authentication')

    def test_registered_user_hit_not_counted(self):
        """
        Test Multiple AnonymousUser Hit, not counted
        """
        self.request_post.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, 'Hit counted: user authentication')

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, 'Not counted: authenticated user has active hit')

    def test_registered_user_hit_counted_after_filter_active(self):
        """
        Test Multiple AnonymousUser Hit, counted because of filter active
        """
        self.request_post.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')

        # create a Hit ten days ago
        created = timezone.now() - timedelta(days=10)
        with patch('django.utils.timezone.now') as mock_now:
            mock_now.return_value = created

            response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, 'Hit counted: user authentication')

        # test a Hit today, within the filter time
        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, True)
        self.assertEqual(response.hit_message, 'Hit counted: user authentication')

    def test_hits_per_ip_limit(self):
        """
        Test `HITCOUNT_HITS_PER_IP_LIMIT` setting.  Should allow multiple hits
        from the same IP until the limit is reached from that IP.
        """
        with patch.object(settings, 'HITCOUNT_HITS_PER_IP_LIMIT', 2):
            responses = []
            for _ in range(3):
                # need a new session key each time.
                engine = import_module(settings.SESSION_ENGINE)
                store = engine.SessionStore()
                store.save()
                self.request_post.session = store
                responses.append(HitCountViewMixin.hit_count(self.request_post, self.hit_count))

        self.assertIs(responses[0].hit_counted, True)
        self.assertEqual(responses[0].hit_message, 'Hit counted: session key')
        self.assertIs(responses[1].hit_counted, True)
        self.assertEqual(responses[1].hit_message, 'Hit counted: session key')
        self.assertIs(responses[2].hit_counted, False)
        self.assertEqual(responses[2].hit_message, 'Not counted: hits per IP address limit reached')
        # test database changes
        hit_count = HitCount.objects.get(pk=self.hit_count.pk)

        self.assertEqual(hit_count.hits, 2)

    def test_exclude_user_group(self):
        with patch.object(settings, 'HITCOUNT_EXCLUDE_USER_GROUP', ('Admin',)):
            self.request_post.user = User.objects.create_user('john', 'lennon@thebeatles.com', 'johnpassword')
            group = Group.objects.create(name='Admin')
            group.user_set.add(self.request_post.user)

            response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)

            self.assertIs(response.hit_counted, False)
            self.assertEqual(response.hit_message, 'Not counted: user group has been excluded')

    def test_blocking_ip(self):
        BlockedIP.objects.create(ip="127.0.0.1")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, 'Not counted: user IP has been blocked')

    def test_blocking_user_agent(self):
        BlockedUserAgent.objects.create(user_agent="my_clever_agent")

        response = HitCountViewMixin.hit_count(self.request_post, self.hit_count)
        self.assertIs(response.hit_counted, False)
        self.assertEqual(response.hit_message, 'Not counted: user agent has been blocked')


class UpdateHitCountJSONTests(HitCountTestBase):

    def test_require_ajax(self):
        """
        Test require ajax request or raise 404
        """
        non_ajax_request = self.factory.get('/')
        with self.assertRaises(Http404):
            HitCountJSONView.as_view()(non_ajax_request)

    def test_require_post_only(self):
        """
        Test require POST request or raise 404
        """
        non_ajax_request = self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        non_ajax_request.session = self.store
        response = HitCountJSONView.as_view()(non_ajax_request)
        json_response = json.loads(response.content.decode())
        json_expects = json.loads('{"error_message": "Hits counted via POST only.", "success": false}')
        self.assertEqual(json_response, json_expects)

    def test_count_hit(self):
        """
        Test a valid request.
        """
        response = HitCountJSONView.as_view()(self.request_post)
        self.assertEqual(response.content, b'{"hit_counted": true, "hit_message": "Hit counted: session key"}')

    def test_count_hit_invalid_hitcount_pk(self):
        """
        Test a valid request with an invalid hitcount pk.
        """
        wrong_pk_request = self.factory.post(
            '/', {'hitcountPK': 15},
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT='my_clever_agent',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        wrong_pk_request.session = self.store

        response = HitCountJSONView.as_view()(wrong_pk_request)

        self.assertEqual(response.content, b'HitCount object_pk not present.')


class UpdateHitCountView(HitCountTestBase):

    def test_count_hit(self):
        """
        Test a valid request.
        """
        view = HitCountDetailView.as_view(model=Post)
        response = view(self.request_get, pk=self.post.pk)
        self.assertEqual(response.context_data['hitcount']['pk'], self.hit_count.pk)
        self.assertEqual(response.context_data['hitcount']['total_hits'], 0)

    def test_count_hit_incremented(self):
        """
        Increment a hit and then get the response.
        """
        view = HitCountDetailView.as_view(model=Post, count_hit=True)
        response = view(self.request_get, pk=self.post.pk)
        self.assertEqual(response.context_data['hitcount']['total_hits'], 1)
        self.assertEqual(response.context_data['hitcount']['pk'], self.hit_count.pk)

    def test_count_hit_incremented_only_once(self):
        """
        Increment a hit and then get the response.
        """
        view = HitCountDetailView.as_view(model=Post, count_hit=True)
        response = view(self.request_get, pk=self.post.pk)
        self.assertEqual(response.context_data['hitcount']['total_hits'], 1)
        self.assertEqual(response.context_data['hitcount']['pk'], self.hit_count.pk)
        view = HitCountDetailView.as_view(model=Post, count_hit=True)
        response = view(self.request_get, pk=self.post.pk)
        self.assertEqual(response.context_data['hitcount']['total_hits'], 1)
        self.assertEqual(response.context_data['hitcount']['pk'], self.hit_count.pk)
