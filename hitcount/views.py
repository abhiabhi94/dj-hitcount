from django.http import HttpResponseBadRequest
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView
from django.views.generic import View

from hitcount.mixins import AJAXRequiredMixin
from hitcount.mixins import HitCountViewMixin
from hitcount.utils import get_hitcount_model


HitCount = get_hitcount_model()


class HitCountJSONView(AJAXRequiredMixin, HitCountViewMixin, View):
    """
    JSON response view to handle HitCount POST.
    """
    def get(self, request, *args, **kwargs):
        msg = _("Hits counted via POST only.")
        return JsonResponse({'success': False, 'error_message': msg})

    def post(self, request, *args, **kwargs):
        hitcount_pk = request.POST.get('hitcountPK')

        try:
            hitcount = HitCount.objects.get(pk=hitcount_pk)
        except HitCount.DoesNotExist:
            return HttpResponseBadRequest(_("HitCount object_pk not present."))

        hit_count_response = self.hit_count(request, hitcount)
        return JsonResponse(hit_count_response._asdict())


class HitCountDetailView(DetailView, HitCountViewMixin):
    """
    HitCountDetailView provides an inherited DetailView that will inject the
    template context with a `hitcount` variable giving you the number of
    Hits for an object without using a template tag.

    Optionally, by setting `count_hit = True` you can also do the business of
    counting the Hit for this object (in lieu of using JavaScript).  It will
    then further inject the response from the attempt to count the Hit into
    the template context.
    """
    count_hit = False

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        assert self.object, 'The object for Detail view has not been defined'

        hit_count = HitCount.objects.get_for_object(self.object)
        hits = hit_count.hits
        context['hitcount'] = {'pk': hit_count.pk}

        if self.count_hit:
            hit_count_response = self.hit_count(self.request, hit_count)
            if hit_count_response.hit_counted:
                hits = hits + 1
            context['hitcount']['hit_counted'] = hit_count_response.hit_counted
            context['hitcount']['hit_message'] = hit_count_response.hit_message

        context['hitcount']['total_hits'] = hits

        return context
