# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.dispatch import receiver
from django.dispatch import Signal


delete_hit_count = Signal()


@receiver(delete_hit_count)
def delete_hit_count_handler(sender, instance, *, save_hitcount=False, **kwargs):
    """
    Custom callback for the Hit.delete() method.

    Hit.delete(): removes the hit from the associated HitCount object.
    Hit.delete(save_hitcount=True): preserves the hit for the associated
    HitCount object.
    """
    if not save_hitcount:
        instance.hitcount.decrease()
