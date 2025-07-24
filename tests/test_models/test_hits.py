from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from blog.models import Post
from hitcount.models import Hit
from hitcount.utils import get_hitcount_model


HitCount = get_hitcount_model()


class TestHitModel(TestCase):
    def setUp(self):
        post = Post.objects.create(title="my title", content="my text")
        hit_count = HitCount.objects.create(content_object=post)
        self.hit = Hit.objects.create(hitcount=hit_count)

    def test_string_representation(self):
        self.assertEqual(str(self.hit), f"Hit: {self.hit.pk}")

    def test_save_does_not_increases_hitcount_for_already_created_obj(self):
        hit_count = HitCount.objects.last()
        init_count = hit_count.hits

        self.hit.save()
        hit_count.refresh_from_db()

        self.assertEqual(hit_count.hits, init_count)

    def test_save_increases_hitcount_for_newly_created_obj(self):
        hit_count = HitCount.objects.last()
        init_count = hit_count.hits

        Hit.objects.create(hitcount=hit_count)
        hit_count.refresh_from_db()

        self.assertEqual(hit_count.hits, init_count + 1)

    def test_hit_count_increase(self):
        """
        Testing if Hit creation triggers increase of associated HitCount

        """
        hit_count = HitCount.objects.last()

        self.assertEqual(hit_count.hits, 1)

        Hit.objects.create(hitcount=hit_count)

        hit_count.refresh_from_db()

        self.assertEqual(hit_count.hits, 2)

    def test_hit_delete(self):
        """
        Testing if Hit deletion triggers decrease of associated HitCount

        """
        self.hit.delete()

        hit_count = HitCount.objects.last()

        self.assertEqual(hit_count.hits, 0)

    def test_hit_delete_save_hitcount(self):
        """
        Testing if Hit deletion with `save_hitcount` flag preserves
        the associated HitCount

        """
        self.hit.delete(save_hitcount=True)

        hit_count = HitCount.objects.last()

        self.assertEqual(hit_count.hits, 1)


class TestHitCountModel(TestCase):
    def setUp(self):
        self.post = Post.objects.create(title="my title", content="my text")

    def test_string_representation(self):
        post = Post.objects.create(title="my title", content="my text")

        hit_count = HitCount(content_object=post)

        self.assertEqual(str(hit_count), "Post title: my title")

    def test_increase(self):
        hit_count = HitCount.objects.create(content_object=self.post)
        hit_count.increase()

        hit_count.refresh_from_db()

        self.assertEqual(hit_count.hits, 1)

    def test_decrease(self):
        hit_count = HitCount.objects.create(hits=1, content_object=self.post)
        hit_count.decrease()

        hit_count.refresh_from_db()

        self.assertEqual(hit_count.hits, 0)

    def test_hits_in_last_assert_error_when_no_args(self):
        hit_count = HitCount.objects.create(content_object=self.post)
        with self.assertRaises(AssertionError):
            hit_count.hits_in_last()

    def test_hits_in_last(self):
        hit_count = HitCount.objects.create(content_object=self.post)

        for x in range(10):
            created = timezone.now() - timedelta(days=x * 5)
            with patch("django.utils.timezone.now") as mock_now:
                mock_now.return_value = created

                Hit.objects.create(hitcount=hit_count)

        hit_count = HitCount.objects.last()

        self.assertEqual(hit_count.hits_in_last(days=30), 6)

    def test_mixin(self):
        hit_count = HitCount.objects.create(content_object=self.post)
        hit_count.increase()

        self.assertEqual(HitCount.objects.get_for_object(self.post).hits, self.post.hit_count.hits)

    def test_mixing_hits_in_last(self):
        """
        Test HitCountMixin `hits_in_last` function.

        """
        hit_count = HitCount.objects.create(content_object=self.post)

        for x in range(10):
            created = timezone.now() - timedelta(days=x * 5)
            with patch("django.utils.timezone.now") as mock_now:
                mock_now.return_value = created

                Hit.objects.create(hitcount=hit_count)

        self.assertEqual(self.post.hit_count.hits_in_last(days=30), 6)

    def test_on_delete_cascade(self):
        """
        Test on_delete=models.CASCADE to ensure that a deleted hitcount
        also removes the related Hits.

        """
        hit_count = HitCount.objects.create(content_object=self.post)

        for _ in range(10):
            Hit.objects.create(hitcount=hit_count)

        self.assertEqual(Hit.objects.all().count(), 10)
        hit_count.delete()

        self.assertEqual(HitCount.objects.all().count(), 0)
        self.assertEqual(Hit.objects.all().count(), 0)
