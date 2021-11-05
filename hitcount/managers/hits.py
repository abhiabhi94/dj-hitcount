from datetime import timedelta

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from hitcount.conf import settings


class HitCountManager(models.Manager):

    def get_for_object(self, obj):
        ctype = ContentType.objects.get_for_model(obj)
        hit_count, created = self.get_or_create(
            content_type=ctype, object_pk=obj.pk)
        return hit_count


class HitManager(models.Manager):

    def filter_active(self, *args, **kwargs):
        """
        Return only the 'active' hits.

        How you count a hit/view will depend on personal choice: Should the
        same user/visitor *ever* be counted twice?  After a week, or a month,
        or a year, should their view be counted again?

        The default is to consider a visitor's hit still 'active' if they
        return within a the last seven days..  After that the hit
        will be counted again.  So if one person visits once a week for a year,
        they will add 52 hits to a given object.

        Change how long the expiration is by adding to settings.py:

        HITCOUNT_KEEP_HIT_ACTIVE  = {'days' : 30, 'minutes' : 30}

        Accepts days, seconds, microseconds, milliseconds, minutes,
        hours, and weeks.  It's creating a datetime.timedelta object.

        """
        grace = settings.HITCOUNT_KEEP_HIT_ACTIVE
        period = timezone.now() - timedelta(**grace)
        return self.filter(created__gte=period).filter(*args, **kwargs)

    def has_limit_reached_by_ip(self, ip=None):
        hits_per_ip_limit = settings.HITCOUNT_HITS_PER_IP_LIMIT
        if not ip or not hits_per_ip_limit:
            return False

        return self.filter_active(ip=ip).count() >= hits_per_ip_limit

    def has_limit_reached_by_session(self, session, hitcount):
        hits_per_session_limit = settings.HITCOUNT_HITS_PER_SESSION_LIMIT
        if not hits_per_session_limit:
            return False

        return self.filter_active(session=session, hitcount=hitcount).count() >= hits_per_session_limit
