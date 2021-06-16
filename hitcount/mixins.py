from collections import namedtuple

from django.contrib.auth.models import ContentType

from hitcount.conf import settings
from hitcount.models import BlockedIP
from hitcount.models import BlockedUserAgent
from hitcount.models import Hit
from hitcount.utils import get_hitcount_model
from hitcount.utils import get_ip


class HitCountModelMixin:
    """
    HitCountMixin provides an easy way to add a `hit_count` property to your
    model that will return the related HitCount object.
    """

    @property
    def hit_count(self):
        ctype = ContentType.objects.get_for_model(self.__class__)
        HitCount = get_hitcount_model()
        hit_count, __ = HitCount.objects.get_or_create(content_type=ctype, object_pk=self.pk)
        return hit_count


class HitCountViewMixin:
    """
    Mixin to evaluate a HttpRequest and a HitCount and determine whether or not
    the HitCount should be incremented and the Hit recorded.
    """

    @staticmethod
    def hit_count(request, hitcount):
        """
        Called with a HttpRequest and HitCount object it will return a
        namedtuple:

        UpdateHitCountResponse(hit_counted=Boolean, hit_message='Message').

        `hit_counted` will be True if the hit was counted and False if it was
        not.  `'hit_message` will indicate by what means the Hit was either
        counted or ignored.
        """
        UpdateHitCountResponse = namedtuple(
            'UpdateHitCountResponse', 'hit_counted hit_message')

        # as of Django 1.8.4 empty sessions are not being saved
        # https://code.djangoproject.com/ticket/25489
        if request.session.session_key is None:
            request.session.save()

        user = request.user

        if settings.HITCOUNT_USE_IP:
            ip = get_ip(request)
        else:
            ip = None
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:255]

        # first, check our request against the IP blocked
        if ip:
            if BlockedIP.objects.filter_ip(ip).exists():
                return UpdateHitCountResponse(False, 'Not counted: user IP has been blocked')

        # second, check our request against the user agent blocked
        if BlockedUserAgent.objects.filter_user_agent(user_agent).exists():
            return UpdateHitCountResponse(False, 'Not counted: user agent has been blocked')

        # third, see if we are excluding a specific user group or not
        exclude_user_group = settings.HITCOUNT_EXCLUDE_USER_GROUP
        if exclude_user_group and request.user.is_authenticated:
            if request.user.groups.filter(name__in=exclude_user_group):
                return UpdateHitCountResponse(False, 'Not counted: user group has been excluded')

        # eliminated first three possible exclusions, now on to checking our database of
        # active hits to see if we should count another one

        # start with a fresh active query set (HITCOUNT_KEEP_HIT_ACTIVE)
        active_hits_qs = Hit.objects.filter_active()

        # check limit on hits from a unique ip address (HITCOUNT_HITS_PER_IP_LIMIT)
        hits_per_ip_limit = settings.HITCOUNT_HITS_PER_IP_LIMIT
        if ip and hits_per_ip_limit:
            if active_hits_qs.filter(ip=ip).count() >= hits_per_ip_limit:
                return UpdateHitCountResponse(
                    False, 'Not counted: hits per IP address limit reached')

        session_key = request.session.session_key
        # create a generic Hit object with request data
        hit = Hit(
            session=session_key,
            hitcount=hitcount,
            ip=ip,
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:255],
        )

        # first, use a user's authentication to see if they made an earlier hit
        if request.user.is_authenticated:
            if not active_hits_qs.filter(user=user).filter(hitcount=hitcount).exists():
                hit.user = user  # associate this hit with a user
                hit.save()

                response = UpdateHitCountResponse(
                    True, 'Hit counted: user authentication')
            else:
                response = UpdateHitCountResponse(
                    False, 'Not counted: authenticated user has active hit')

        # if not authenticated, see if we have a repeat session
        else:
            if not active_hits_qs.filter(session=session_key).filter(hitcount=hitcount).exists():
                hit.save()
                response = UpdateHitCountResponse(True, 'Hit counted: session key')
            else:
                response = UpdateHitCountResponse(False, 'Not counted: session key has active hit')

        return response
