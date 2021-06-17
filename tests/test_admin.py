from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import PermissionDenied
from django.test import RequestFactory
from django.test import SimpleTestCase
from django.test import TestCase
from django.urls import reverse

from blog.models import Post
from hitcount.admin import HitAdmin
from hitcount.admin import HitCountAdmin
from hitcount.models import BlockedIP
from hitcount.models import BlockedUserAgent
from hitcount.models import Hit
from hitcount.utils import get_hitcount_model


HitCount = get_hitcount_model()


class TestHitCountAdmin(SimpleTestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = HitCountAdmin(HitCount, AdminSite())

    def test_has_add_permission_is_always_false(self):
        self.assertIs(self.admin.has_add_permission(self.factory), False)


class TestHitAdmin(TestCase):

    def setUp(self):
        self.factory = RequestFactory()
        self.admin = HitAdmin(Hit, AdminSite())
        self.request = self.factory.get(reverse('admin:hitcount_hit_changelist'))

        # https://code.djangoproject.com/ticket/17971
        self.request.session = 'session'
        messages = FallbackStorage(self.request)
        self.request._messages = messages

        post = Post.objects.create(title='my title', content='my text')
        hit_count = HitCount.objects.create(content_object=post)

        for x in range(10):
            Hit.objects.create(hitcount=hit_count, ip="127.0.0.%s" % x, user_agent="agent_%s" % x)

    def test_has_add_permission(self):
        self.assertIs(self.admin.has_add_permission(self.factory), False)

    def test_get_actions_removes_delete_selected_method(self):
        """
        Actions should be: ['block_ips',
               'block_user_agents',
               'block_and_delete_ips',
               'block_and_delete_user_agents',
               'delete_queryset',
               ]
        """
        self.request.user = User.objects.create_superuser(username='admin', password='admin', email='a@a.com')

        self.assertIs('delete_selected' not in self.admin.get_actions(self.request), True)

    def test_get_actions_methods(self):
        """
        Actions should be: ['block_ips',
               'block_user_agents',
               'block_and_delete_ips',
               'block_and_delete_user_agents',
               'delete_queryset',
               ]
        """
        self.request.user = AnonymousUser()
        actions = [
            'block_ips',
            'block_user_agents',
            'block_and_delete_ips',
            'block_and_delete_user_agents',
            'delete_queryset',
        ]

        self.assertEqual(actions, list(self.admin.get_actions(self.request).keys()))

    def test_block_ips_single(self):
        qs = Hit.objects.filter(ip="127.0.0.5")

        self.admin.block_ips(self.request, qs)

        ip = BlockedIP.objects.last()

        self.assertEqual(ip.ip, "127.0.0.5")
        self.assertEqual(BlockedIP.objects.all().count(), 1)

    def test_block_ips_multiple(self):
        """
        Test adding `block_ips` via Admin action with multiple items.
        """
        qs = Hit.objects.all()[:5]

        self.admin.block_ips(self.request, qs)
        ips = BlockedIP.objects.values_list('ip', flat=True)

        self.assertEqual(ips[4], '127.0.0.5')
        self.assertEqual(BlockedIP.objects.all().count(), 5)

    def test_block_ips_add_only_once(self):
        """
        Test adding `block_ips` to ensure adding the same IP address more
        than once does not duplicate a record in the BlockedIP table.
        """
        ip = '127.0.0.5'

        qs = Hit.objects.filter(ip=ip)
        self.admin.block_ips(self.request, qs)

        self.assertEqual(BlockedIP.objects.all().count(), 1)

        # adding a second time should not increase the list
        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.block_ips(self.request, qs)

        self.assertEqual(BlockedIP.objects.all().count(), 1)

    def test_block_user_agents_single(self):
        qs = Hit.objects.filter(ip="127.0.0.5")

        self.admin.block_user_agents(self.request, qs)
        ua = BlockedUserAgent.objects.last()

        self.assertEqual(ua.user_agent, 'agent_5')
        self.assertEqual(BlockedUserAgent.objects.all().count(), 1)

    def test_block_user_agents_multiple(self):
        qs = Hit.objects.all()[:5]

        self.admin.block_user_agents(self.request, qs)
        uas = BlockedUserAgent.objects.values_list('user_agent', flat=True)

        self.assertEqual(uas[2], 'agent_7')
        self.assertEqual(BlockedUserAgent.objects.all().count(), 5)

    def test_block_user_agents_add_only_once(self):
        """
        Test adding `block_ips` to ensure adding the same user agent more
        than once does not duplicate a record in the BlockedUserAgent table.
        """
        ip = '127.0.0.5'
        qs = Hit.objects.filter(ip=ip)

        self.admin.block_user_agents(self.request, qs)

        self.assertEqual(BlockedUserAgent.objects.all().count(), 1)

        # adding a second time should not increase the list
        qs = Hit.objects.filter(ip=ip)

        self.admin.block_user_agents(self.request, qs)

        self.assertEqual(BlockedUserAgent.objects.all().count(), 1)

    def test_delete_queryset(self):
        my_admin = User.objects.create_superuser('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.all()[:5]
        self.admin.delete_queryset(self.request, qs)
        hit_count = HitCount.objects.last()

        self.assertEqual(Hit.objects.all().count(), 5)
        self.assertEqual(hit_count.hits, 5)

    def test_delete_queryset_single_item(self):
        my_admin = User.objects.create_superuser('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.filter(ip="127.0.0.5")
        self.admin.delete_queryset(self.request, qs)
        hit_count = HitCount.objects.last()

        self.assertEqual(Hit.objects.all().count(), 9)
        self.assertEqual(hit_count.hits, 9)

    def test_delete_queryset_permission_denied(self):
        my_admin = User.objects.create_user('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.all()[:5]
        with self.assertRaises(PermissionDenied):
            self.admin.delete_queryset(self.request, qs)

    def test_block_and_delete_ips(self):
        my_admin = User.objects.create_superuser('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.all()[:5]
        self.admin.block_and_delete_ips(self.request, qs)
        hit_count = HitCount.objects.last()

        self.assertEqual(Hit.objects.all().count(), 5)
        self.assertEqual(hit_count.hits, 5)
        self.assertEqual(BlockedIP.objects.all().count(), 5)

    def test_block_and_delete_user_agents(self):
        my_admin = User.objects.create_superuser('myuser', 'myemail@example.com', '1234')
        self.request.user = my_admin

        qs = Hit.objects.all()[:5]
        self.admin.block_and_delete_user_agents(self.request, qs)
        hit_count = HitCount.objects.last()

        self.assertEqual(Hit.objects.all().count(), 5)
        self.assertEqual(hit_count.hits, 5)
        self.assertEqual(BlockedUserAgent.objects.all().count(), 5)
