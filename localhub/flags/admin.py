# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from localhub.flags.models import Flag


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    raw_id_fields = ("user", "moderator")
    list_display = ("user", "community", "content_type", "reason")
    ordering = ("-created",)
    list_select_related = ("community", "content_type", "user")
