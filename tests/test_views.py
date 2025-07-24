import json
from importlib import import_module
from unittest.mock import patch

from django.contrib.auth.models import AnonymousUser
from django.http import Http404
from django.test import RequestFactory
from django.test import TestCase

from blog.models import Post
from hitcount.conf import settings
from hitcount.utils import get_hitcount_model
from hitcount.views import HitCountDetailView
from hitcount.views import HitCountJSONView

HitCount = get_hitcount_model()


class BaseHitCountViewTest(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title="my title", content="my text")
        self.hit_count = HitCount.objects.create(content_object=self.post)
        self.factory = RequestFactory()
        self.request_post = self.factory.post(
            "/",
            {"hitcountPK": self.hit_count.pk},
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="my_clever_agent",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        self.request_get = self.factory.get(
            "/", REMOTE_ADDR="127.0.0.1", HTTP_USER_AGENT="my_clever_agent", HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        self.engine = import_module(settings.SESSION_ENGINE)
        self.store = self.engine.SessionStore()
        self.store.save()
        self.request_post.session = self.store
        self.request_post.user = AnonymousUser()
        self.request_get.session = self.store
        self.request_get.user = AnonymousUser()


class TestHitCountJSONView(BaseHitCountViewTest):
    def test_require_ajax(self):
        non_ajax_request = self.factory.get("/")
        with self.assertRaises(Http404):
            HitCountJSONView.as_view()(non_ajax_request)

    def test_require_post_only(self):
        """
        Test require POST request or raise 404
        """
        non_ajax_request = self.factory.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
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
            "/",
            {"hitcountPK": 15},
            REMOTE_ADDR="127.0.0.1",
            HTTP_USER_AGENT="my_clever_agent",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        wrong_pk_request.session = self.store

        response = HitCountJSONView.as_view()(wrong_pk_request)

        self.assertEqual(response.content, b"HitCount object_pk not present.")


class TestHitCountDetailView(BaseHitCountViewTest):
    def test_count_hit(self):
        """
        Test a valid request.
        """
        view = HitCountDetailView.as_view(model=Post)

        response = view(self.request_get, pk=self.post.pk)

        self.assertEqual(response.context_data["hitcount"]["pk"], self.hit_count.pk)
        self.assertEqual(response.context_data["hitcount"]["total_hits"], 0)

    def test_count_hit_incremented(self):
        """
        Increment a hit and then get the response.
        """
        view = HitCountDetailView.as_view(model=Post, count_hit=True)

        response = view(self.request_get, pk=self.post.pk)

        self.assertEqual(response.context_data["hitcount"]["total_hits"], 1)
        self.assertEqual(response.context_data["hitcount"]["pk"], self.hit_count.pk)

    @patch.object(settings, "HITCOUNT_HITS_PER_SESSION_LIMIT", 1)
    def test_count_hit_incremented_only_once(self):
        """
        Increment a hit and then get the response.
        """
        view = HitCountDetailView.as_view(model=Post, count_hit=True)

        response = view(self.request_get, pk=self.post.pk)

        self.assertEqual(response.context_data["hitcount"]["total_hits"], 1)
        self.assertEqual(response.context_data["hitcount"]["pk"], self.hit_count.pk)
        view = HitCountDetailView.as_view(model=Post, count_hit=True)

        response = view(self.request_get, pk=self.post.pk)

        self.assertEqual(response.context_data["hitcount"]["total_hits"], 1)
        self.assertEqual(response.context_data["hitcount"]["pk"], self.hit_count.pk)
