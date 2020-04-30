# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value
from django.template.response import TemplateResponse
from django.views.generic import ListView

from taggit.models import Tag

from localhub.activities.views.streams import BaseActivityStreamView
from localhub.common.views import ParentObjectMixin, SearchMixin

from .mixins import TagQuerySetMixin


class BaseTagListView(TagQuerySetMixin, ListView):
    def get_queryset(self):
        return super().get_queryset().order_by("name")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["content_warnings"] = [
            tag.strip().lower()[1:]
            for tag in self.request.community.content_warning_tags.split()
        ]
        return data


class TagAutocompleteListView(BaseTagListView):
    template_name = "hashtags/tag_autocomplete_list.html"
    exclude_unused_tags = True

    def get_queryset(self):
        search_term = self.request.GET.get("q", "").strip()
        if not search_term:
            return Tag.objects.none()
        return super().get_queryset().filter(name__istartswith=search_term)


tag_autocomplete_list_view = TagAutocompleteListView.as_view()


class TagListView(SearchMixin, BaseTagListView):
    template_name = "hashtags/tag_list.html"
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE
    exclude_unused_tags = True

    def get_queryset(self):

        qs = super().get_queryset()

        if self.search_query:
            qs = qs.filter(name__icontains=self.search_query)

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_following=Exists(
                    self.request.user.following_tags.filter(pk=OuterRef("id"))
                )
            )
        else:
            qs = qs.annotate(is_following=Value(False, BooleanField()))

        qs = qs.annotate(
            item_count=Count(
                "taggit_taggeditem_items",
                filter=Q(taggit_taggeditem_items__pk__in=self.get_tagged_items()),
            )
        )

        return qs.order_by("-item_count", "name")


tag_list_view = TagListView.as_view()


class FollowingTagListView(BaseTagListView):
    template_name = "hashtags/following_tag_list.html"

    def get_queryset(self):
        return self.request.user.following_tags.order_by("name")


following_tag_list_view = FollowingTagListView.as_view()


class BlockedTagListView(BaseTagListView):
    template_name = "hashtags/blocked_tag_list.html"

    def get_queryset(self):
        return self.request.user.blocked_tags.order_by("name")


blocked_tag_list_view = BlockedTagListView.as_view()


class TagDetailView(ParentObjectMixin, BaseActivityStreamView):
    template_name = "hashtags/tag_detail.html"
    ordering = "-created"

    parent_model = Tag
    parent_object_name = "tag"
    parent_required = False

    def get(self, request, *args, **kwargs):
        if self.tag is None:
            return TemplateResponse(
                request, "hashtags/not_found.html", {"tag": kwargs["slug"]}, status=404,
            )
        return super().get(request, *args, **kwargs)

    def filter_queryset(self, queryset):
        qs = (
            super()
            .filter_queryset(queryset)
            .exclude_blocked_users(self.request.user)
            .published_or_owner(self.request.user)
            .filter(tags__name__in=[self.tag.name])
            .distinct()
        )

        # ensure we block all unwanted tags *unless* it's the tag
        # in question.
        if self.request.user.is_authenticated:
            qs = qs.exclude(
                Q(tags__in=self.request.user.blocked_tags.exclude(id=self.tag.id)),
                ~Q(owner=self.request.user),
            )
        return qs


tag_detail_view = TagDetailView.as_view()
