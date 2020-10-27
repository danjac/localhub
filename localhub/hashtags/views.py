# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import operator
from functools import reduce

# Django
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

# Third Party Libraries
from taggit.models import Tag, TaggedItem

# Localhub
from localhub.activities.utils import get_activity_models
from localhub.activities.views.streams import BaseActivityStreamView
from localhub.communities.mixins import (
    CommunityPermissionRequiredMixin,
    CommunityRequiredMixin,
)
from localhub.views import ParentObjectMixin, SearchMixin, SuccessActionView


class TagQuerySetMixin(CommunityRequiredMixin):

    model = Tag

    # if True, only those tags used in this community by activities
    # will be included
    exclude_unused_tags = False

    def get_tagged_items(self):
        q = Q(
            reduce(
                operator.or_,
                [
                    Q(
                        object_id__in=model.objects.filter(
                            community=self.request.community
                        ).values("id"),
                        content_type=content_type,
                    )
                    for model, content_type in ContentType.objects.get_for_models(
                        *get_activity_models()
                    ).items()
                ],
            )
        )
        return TaggedItem.objects.filter(q)

    def get_queryset(self):
        if self.exclude_unused_tags:
            return Tag.objects.filter(
                taggit_taggeditem_items__in=self.get_tagged_items()
            ).distinct()
        return super().get_queryset()


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
    template_name = "hashtags/list/autocomplete.html"
    exclude_unused_tags = True

    def get_queryset(self):
        search_term = self.request.GET.get("q", "").strip()
        if not search_term:
            return Tag.objects.none()
        return (
            super()
            .get_queryset()
            .filter(name__istartswith=search_term)[: settings.DEFAULT_PAGE_SIZE]
        )


tag_autocomplete_list_view = TagAutocompleteListView.as_view()


class TagListView(SearchMixin, BaseTagListView):
    template_name = "hashtags/list/all.html"
    paginate_by = settings.LONG_PAGE_SIZE
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
    template_name = "hashtags/list/following.html"

    def get_queryset(self):
        return self.request.user.following_tags.order_by("name")


following_tag_list_view = FollowingTagListView.as_view()


class BlockedTagListView(BaseTagListView):
    template_name = "hashtags/list/blocked.html"

    def get_queryset(self):
        return self.request.user.blocked_tags.order_by("name")


blocked_tag_list_view = BlockedTagListView.as_view()


class TagDetailView(ParentObjectMixin, BaseActivityStreamView):
    template_name = "hashtags/tag_detail.html"
    ordering = "-created"

    parent_model = Tag
    parent_context_object_name = "tag"
    parent_required = False

    def get(self, request, *args, **kwargs):
        if self.parent is None:
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
            .filter(tags__name__in=[self.parent.name])
            .distinct()
        )

        # ensure we block all unwanted tags *unless* it's the tag
        # in question.
        if self.request.user.is_authenticated:
            qs = qs.exclude(
                Q(tags__in=self.request.user.blocked_tags.exclude(id=self.parent.id)),
                ~Q(owner=self.request.user),
            )
        return qs


tag_detail_view = TagDetailView.as_view()


class BaseTagActionView(
    TagQuerySetMixin, CommunityPermissionRequiredMixin, SuccessActionView
):
    ...


class BaseTagFollowView(BaseTagActionView):
    permission_required = "users.follow_tag"
    is_success_ajax_response = True
    success_template_name = "hashtags/includes/follow.html"


class TagFollowView(BaseTagFollowView):
    success_message = _("You are now following #%(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following_tags.add(self.object)
        return self.success_response()

    def get_success_context_data(self):
        return {**super().get_success_context_data(), "is_following": True}


tag_follow_view = TagFollowView.as_view()


class TagUnfollowView(BaseTagFollowView):
    success_message = _("You are no longer following #%(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following_tags.remove(self.object)
        return self.success_response()

    def get_success_context_data(self):
        return {**super().get_success_context_data(), "is_following": False}


tag_unfollow_view = TagUnfollowView.as_view()


class BaseTagBlockView(BaseTagActionView):
    permission_required = "users.block_tag"
    is_success_ajax_response = True
    success_template_name = "hashtags/includes/block.html"


class TagBlockView(BaseTagBlockView):
    success_message = _("You are now blocking #%(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.blocked_tags.add(self.object)
        return self.success_response()

    def get_success_context_data(self):
        return {**super().get_success_context_data(), "is_blocked": True}


tag_block_view = TagBlockView.as_view()


class TagUnblockView(BaseTagBlockView):
    success_message = _("You are no longer blocking #%(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.blocked_tags.remove(self.object)
        return self.success_response()

    def get_success_context_data(self):
        return {**super().get_success_context_data(), "is_blocked": False}


tag_unblock_view = TagUnblockView.as_view()
