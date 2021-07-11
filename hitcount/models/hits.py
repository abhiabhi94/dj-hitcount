from datetime import timedelta

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from hitcount.conf import settings
from hitcount.managers import HitCountManager
from hitcount.managers import HitManager
from hitcount.signals import delete_hit_count


class HitCountBase(models.Model):
    """
    Base class for hitcount models.

    Model that stores the hit totals for any content object.

    """
    hits = models.PositiveIntegerField(default=0)
    modified = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey(
        ContentType, related_name="content_type_set_for_%(class)s", on_delete=models.CASCADE)
    object_pk = models.PositiveIntegerField(verbose_name='object ID')
    content_object = GenericForeignKey('content_type', 'object_pk')

    objects = HitCountManager()

    class Meta:
        abstract = True
        ordering = ('-hits',)
        get_latest_by = "modified"
        verbose_name = _("hit count")
        verbose_name_plural = _("hit counts")
        unique_together = ("content_type", "object_pk")

    def __str__(self):
        return '%s' % self.content_object

    def increase(self):
        self.hits = F('hits') + 1
        self.save(update_fields=['hits'])

    def decrease(self):
        self.hits = F('hits') - 1
        self.save(update_fields=['hits'])

    def hits_in_last(self, **kwargs):
        """
        Returns hit count for an object during a given time period.

        This will only work for as long as hits are saved in the Hit database.
        If you are purging your database after 45 days, for example, that means
        that asking for hits in the last 60 days will return an incorrect
        number as that the longest period it can search will be 45 days.

        For example: hits_in_last(days=7).

        Accepts days, seconds, microseconds, milliseconds, minutes,
        hours, and weeks.  It's creating a datetime.timedelta object.

        """
        assert kwargs, "Must provide at least one timedelta arg (eg, days=1)"

        period = timezone.now() - timedelta(**kwargs)
        return self.hit_set.filter(created__gte=period).count()

    # def get_content_object_url(self):
    #     """
    #     Django has this in its contrib.comments.model file -- seems worth
    #     implementing though it may take a couple steps.
    #
    #     """
    #     pass


class HitCount(HitCountBase):
    """Built-in hitcount class. Default functionality."""

    class Meta(HitCountBase.Meta):
        db_table = "hitcount_hit_count"


class Hit(models.Model):
    """
    Model captures a single Hit by a visitor.

    None of the fields are editable because they are all dynamically created.
    Browsing the Hit list in the Admin will allow one to block both
    IP addresses as well as User Agents. Blocking simply causes those
    hits to not be counted or recorded.

    Depending on how long you set the HITCOUNT_KEEP_HIT_ACTIVE, and how long
    you want to be able to use `HitCount.hits_in_last(days=30)` you can choose
    to clean up your Hit table by using the management `hitcount_cleanup`
    management command.

    """
    created = models.DateTimeField(editable=False, auto_now_add=True, db_index=True)
    ip = models.CharField(max_length=40, editable=False, db_index=True, null=True)
    session = models.CharField(max_length=40, editable=False, db_index=True)
    user_agent = models.CharField(max_length=255, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, editable=False, on_delete=models.CASCADE)
    hitcount = models.ForeignKey(settings.HITCOUNT_HITCOUNT_MODEL, editable=False, on_delete=models.CASCADE)

    objects = HitManager()

    class Meta:
        ordering = ('-created',)
        get_latest_by = 'created'
        verbose_name = _("hit")
        verbose_name_plural = _("hits")

    def __str__(self):
        return 'Hit: %s' % self.pk

    def save(self, *args, **kwargs):
        """
        The first time the object is created and saved, we increment
        the associated HitCount object by one. The opposite applies
        if the Hit is deleted.
        """
        if self.pk is None:
            self.hitcount.increase()

        super().save(*args, **kwargs)

    def delete(self, save_hitcount=False):
        """
        If a Hit is deleted and save_hitcount=True, it will preserve the
        HitCount object's total. However, under normal circumstances, a
        delete() will trigger a subtraction from the HitCount object's total.

        NOTE: This doesn't work at all during a queryset.delete().

        """
        delete_hit_count.send(
            sender=self, instance=self, save_hitcount=save_hitcount)
        super().delete()
