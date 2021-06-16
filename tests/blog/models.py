from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from hitcount.conf import settings as hitcount_settings
from hitcount.mixins import HitCountModelMixin


class Post(models.Model, HitCountModelMixin):
    title = models.CharField(max_length=200)
    content = models.TextField()
    hit_count_generic = GenericRelation(
        hitcount_settings.HITCOUNT_HITCOUNT_MODEL,
        object_id_field='object_pk',
        related_query_name='hit_count_generic_relation'
    )

    def __str__(self):
        return "Post title: %s" % self.title
