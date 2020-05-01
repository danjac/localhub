# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.contrib import admin

from localhub.markdown.admin import MarkdownFieldMixin


class ActivityAdmin(MarkdownFieldMixin, admin.ModelAdmin):

    autocomplete_fields = ("owner", "editor", "community")
    date_hierarchy = "created"
    list_display = ("__str__", "owner", "community", "created", "is_reshare")
    list_filter = ("community",)
    raw_id_fields = ("parent",)
    ordering = ("-created",)
    search_fields = ("search_document", "owner__username")

    def get_search_results(self, request, queryset, search_term):
        if search_term:
            return (
                queryset.search(search_term)
                | queryset.filter(owner__username__icontains=search_term),
                True,
            )
        return super().get_search_results(request, queryset, search_term)
