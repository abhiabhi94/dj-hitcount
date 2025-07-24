from datetime import timedelta

from django.core.management import BaseCommand
from django.utils import timezone

from hitcount.conf import settings
from hitcount.models import Hit


class Command(BaseCommand):
    help = "Can be run as a cronjob or directly to clean out old Hits objects from the database."

    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    def handle(self, *args, **kwargs):
        self.handle_noargs()

    def handle_noargs(self, **options):
        grace = settings.HITCOUNT_KEEP_HIT_IN_DATABASE
        period = timezone.now() - timedelta(**grace)
        qs = Hit.objects.filter(created__lt=period)
        number_removed = qs.count()
        qs.delete()
        self.stdout.write("Successfully removed %s Hits" % number_removed)
