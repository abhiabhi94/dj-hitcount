from datetime import timedelta
from io import StringIO
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from blog.models import Post
from hitcount.conf import settings
from hitcount.models import Hit
from hitcount.utils import get_hitcount_model


HitCount = get_hitcount_model()


@patch.object(settings, 'HITCOUNT_KEEP_HIT_IN_DATABASE', {'days': 30})
class HitCountCleanUp(TestCase):
    COMMAND_NAME = 'hitcount_cleanup'

    def setUp(self):

        post = Post.objects.create(title='hi', content='some text')
        hit_count = HitCount.objects.create(content_object=post)

        for x in range(10):
            created = timezone.now() - timedelta(days=x * 5)
            with patch('django.utils.timezone.now') as mock_now:
                mock_now.return_value = created

                Hit.objects.create(hitcount=hit_count)

    def test_remove_expired_hits(self):
        """There should be only 6 items remaining after cleanup."""
        call_command(self.COMMAND_NAME)

        self.assertEqual(Hit.objects.all().count(), 6)

    def test_preserve_hitcount(self):
        """Removing Hits should not decrease the total HitCount."""
        hit_count = HitCount.objects.get(pk=1)

        call_command(self.COMMAND_NAME)

        self.assertEqual(hit_count.hits, 10)

    def test_standard_output(self):
        out = StringIO()

        call_command(self.COMMAND_NAME, stdout=out)

        self.assertIn('Successfully removed 4 Hits', out.getvalue())
