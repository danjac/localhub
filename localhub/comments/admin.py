# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from localhub.common.markdown.admin import MarkdownFieldMixin
from simple_history.admin import SimpleHistoryAdmin

from .models import Comment


@admin.register(Comment)
class CommentAdmin(MarkdownFieldMixin, SimpleHistoryAdmin):
    raw_id_fields = ("owner",)
    list_display = ("owner", "community", "created")
    ordering = ("-created",)

    def community(self, obj):
        return obj.activity.community.name
