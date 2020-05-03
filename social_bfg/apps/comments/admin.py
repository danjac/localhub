# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib import admin

# Social-BFG
from social_bfg.markdown.admin import MarkdownFieldMixin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(MarkdownFieldMixin, admin.ModelAdmin):
    raw_id_fields = ("owner",)
    list_display = ("owner", "community", "created")
    ordering = ("-created",)

    def community(self, obj):
        return obj.activity.community.name
