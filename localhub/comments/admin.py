# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib import admin

# Localhub
from localhub.common.markdown.admin import MarkdownFieldMixin

# Local
from .models import Comment


@admin.register(Comment)
class CommentAdmin(MarkdownFieldMixin, admin.ModelAdmin):
    raw_id_fields = ("owner",)
    list_display = ("owner", "community", "created")
    ordering = ("-created",)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("community")

    def community(self, obj):
        return obj.community.name
