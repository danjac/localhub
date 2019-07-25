# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from simple_history.admin import SimpleHistoryAdmin

from localhub.comments.models import Comment
from localhub.core.markdown.admin import MarkdownFieldMixin


@admin.register(Comment)
class CommentAdmin(MarkdownFieldMixin, SimpleHistoryAdmin):
    raw_id_fields = ("owner",)
    list_display = ("owner", "community", "created")
    ordering = ("-created",)

    def community(self, obj: Comment) -> str:
        return obj.activity.community.name
