# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from localite.core.markdown.admin import MarkdownFieldMixin


class ActivityAdmin(MarkdownFieldMixin, admin.ModelAdmin):
    raw_id_fields = ("owner",)
    list_display = ("__str__", "owner", "community", "created")
    ordering = ("-created",)
