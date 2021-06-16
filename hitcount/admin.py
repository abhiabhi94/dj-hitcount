# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.utils.translation import gettext_lazy as _

from hitcount.conf import settings
from hitcount.models import BlockedIP
from hitcount.models import BlockedUserAgent
from hitcount.models import Hit
from hitcount.utils import _get_model_from_string


class HitAdmin(admin.ModelAdmin):
    list_display = ('created', 'user', 'ip', 'user_agent', 'hitcount')
    search_fields = ('ip', 'user_agent')
    date_hierarchy = 'created'
    actions = [
        'block_ips',
        'block_user_agents',
        'block_and_delete_ips',
        'block_and_delete_user_agents',
        'delete_queryset',
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request):
        return False

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def block_ips(self, request, queryset):
        for obj in queryset:
            BlockedIP.objects.get_or_create(ip=obj.ip)

        msg = _("Successfully blockeded %d IPs") % queryset.count()
        self.message_user(request, msg)

    block_ips.short_description = _("Block selected IP addresses")

    def block_user_agents(self, request, queryset):
        for obj in queryset:
            BlockedUserAgent.objects.get_or_create(user_agent=obj.user_agent)

        msg = _("Successfully blocked %d User Agents") % queryset.count()
        self.message_user(request, msg)

    block_user_agents.short_description = _("Add selected User Agents to blocked")

    def block_and_delete_ips(self, request, queryset):
        self.block_ips(request, queryset)
        self.delete_queryset(request, queryset)

    block_and_delete_ips.short_description = _("Delete selected hits and block related IP addresses")

    def block_and_delete_user_agents(self, request, queryset):
        self.block_user_agents(request, queryset)
        self.delete_queryset(request, queryset)

    block_and_delete_user_agents.short_description = _("Delete selected hits and block related User Agents")

    def delete_queryset(self, request, queryset):
        if not self.has_delete_permission(request):
            raise PermissionDenied
        else:
            if queryset.count() == 1:
                msg = "1 hit was"
            else:
                msg = "%s hits were" % queryset.count()

            for obj in queryset.iterator():
                obj.delete()  # calling it this way to get custom delete() method

            self.message_user(request, "%s successfully deleted." % msg)
    delete_queryset.short_description = _("Delete selected hits")


admin.site.register(Hit, HitAdmin)


class HitCountAdmin(admin.ModelAdmin):
    list_display = ('content_object', 'hits', 'modified')
    fields = ('hits',)

    def has_add_permission(self, request):
        return False


admin.site.register(_get_model_from_string(settings.HITCOUNT_HITCOUNT_MODEL), HitCountAdmin)


class BlockedIPAdmin(admin.ModelAdmin):
    pass


admin.site.register(BlockedIP, BlockedIPAdmin)


class BlockedUserAgentAdmin(admin.ModelAdmin):
    pass


admin.site.register(BlockedUserAgent, BlockedUserAgentAdmin)
