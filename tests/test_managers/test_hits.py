from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from blog.models import Post
from hitcount.conf import settings
from hitcount.models import Hit
from hitcount.models import HitCount


class TestHitManager(TestCase):
    def setUp(self):
        post = Post.objects.create(title='my title', content='my text')
        hit_count = HitCount.objects.create(content_object=post)
        self.hit = Hit.objects.create(hitcount=hit_count)

    @patch.object(settings, 'HITCOUNT_KEEP_HIT_ACTIVE', {'days': 7})
    def test_filter_active(self):
        """
        Test for "active" Hits.  Out of ten, should have seven remaining.

        """
        hit_count = HitCount.objects.last()

        # add 9 more Hits
        for x in range(9):
            created = timezone.now() - timedelta(days=x + 1)
            with patch('django.utils.timezone.now') as mock_now:
                mock_now.return_value = created

                Hit.objects.create(hitcount=hit_count)

        self.assertEqual(Hit.objects.all().count(), 10)
        self.assertEqual(Hit.objects.filter_active().count(), 7)


class TestHitCountManager(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title='my title', content='my test')

    def test_get_for_object(self):
        post2 = Post.objects.create(title='my title2', content='my text')
        hit_count = HitCount.objects.create(content_object=self.post)
        hit_count2 = HitCount.objects.create(content_object=post2)

        self.assertEqual(HitCount.objects.get_for_object(self.post), hit_count)
        self.assertEqual(HitCount.objects.get_for_object(post2), hit_count2)

    def test_generic_relation(self):
        """
        Test generic relation back to HitCount from a model.

        """
        hit_count = HitCount.objects.create(content_object=self.post)
        hit_count.increase()

        self.assertEqual(
            HitCount.objects.get_for_object(self.post).hits,
            self.post.hit_count_generic.get().hits
        )
