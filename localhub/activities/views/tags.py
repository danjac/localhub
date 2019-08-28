# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import operator

from functools import reduce

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property
from django.urls import reverse

from rules.contrib.views import PermissionRequiredMixin

from taggit.models import Tag, TaggedItem

from vanilla import ListView, GenericModelView

from localhub.activities.views.streams import BaseStreamView
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.views import SearchMixin
from localhub.events.models import Event
from localhub.photos.models import Photo
from localhub.posts.models import Post


class TagQuerySetMixin(CommunityRequiredMixin):
    """
    Only shows tags where content is available within the community.
    """

    tagged_models = [Post, Event, Photo]

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
                    for model, content_type in ContentType.objects.get_for_models(  # noqa
                        *self.tagged_models
                    ).items()
                ],
            )
        )
        return TaggedItem.objects.filter(q)

    def get_queryset(self):
        return Tag.objects.filter(
            taggit_taggeditem_items__in=self.get_tagged_items()
        ).distinct()


class BaseSingleTagView(GenericModelView):
    model = Tag
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


class BaseTagListView(ListView):
    def get_queryset(self):
        return super().get_queryset().order_by("name")


class TagAutocompleteListView(TagQuerySetMixin, BaseTagListView):
    template_name = "activities/tags/tag_autocomplete_list.html"

    def get_queryset(self):
        search_term = self.request.GET.get("q", "").strip()
        if not search_term:
            return Tag.objects.none()
        return super().get_queryset().filter(name__istartswith=search_term)


tag_autocomplete_list_view = TagAutocompleteListView.as_view()


class TagDetailView(BaseStreamView):
    template_name = "activities/tags/tag_detail.html"

    @cached_property
    def tag(self):
        return get_object_or_404(Tag, slug=self.kwargs["slug"])

    def filter_queryset(self, queryset):
        qs = (
            super()
            .filter_queryset(queryset)
            .blocked_users(self.request.user)
            .filter(tags__name__in=[self.tag.name])
            .distinct()
        )

        # ensure we block all unwanted tags *unless* it's the tag
        # in question.
        if self.request.user.is_authenticated:
            qs = qs.exclude(
                Q(
                    tags__in=self.request.user.blocked_tags.exclude(
                        id=self.tag.id
                    )
                ),
                ~Q(owner=self.request.user),
            )
        return qs

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["tag"] = self.tag
        return data


tag_detail_view = TagDetailView.as_view()


class TagFollowView(
    LoginRequiredMixin, PermissionRequiredMixin, BaseSingleTagView
):
    permission_required = "users.follow_tag"

    def get_permission_object(self):
        return self.request.community

    def get_success_url(self):
        return reverse("activities:tag_detail", args=[self.object.slug])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.following_tags.add(self.object)

        return HttpResponseRedirect(self.get_success_url())


tag_follow_view = TagFollowView.as_view()


class TagUnfollowView(LoginRequiredMixin, BaseSingleTagView):
    def get_success_url(self):
        return reverse("activities:tag_detail", args=[self.object.slug])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.following_tags.remove(self.object)
        return HttpResponseRedirect(self.get_success_url())


tag_unfollow_view = TagUnfollowView.as_view()


class TagBlockView(
    LoginRequiredMixin, PermissionRequiredMixin, BaseSingleTagView
):
    permission_required = "users.block_tag"

    def get_permission_object(self):
        return self.request.community

    def get_success_url(self):
        return reverse("activities:tag_detail", args=[self.object.slug])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked_tags.add(self.object)
        return HttpResponseRedirect(self.get_success_url())


tag_block_view = TagBlockView.as_view()


class TagUnblockView(LoginRequiredMixin, BaseSingleTagView):
    def get_success_url(self):
        return reverse("activities:tag_detail", args=[self.object.slug])

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.request.user.blocked_tags.remove(self.object)
        return HttpResponseRedirect(self.get_success_url())


tag_unblock_view = TagUnblockView.as_view()


class TagListView(SearchMixin, TagQuerySetMixin, BaseTagListView):
    template_name = "activities/tags/tag_list.html"
    paginate_by = settings.DEFAULT_PAGE_SIZE * 2

    def get_queryset(self):

        qs = super().get_queryset()

        if self.search_query:
            qs = qs.filter(name__icontains=self.search_query)

        if self.request.user.is_authenticated:
            qs = qs.annotate(
                is_following=Exists(
                    self.request.user.following_tags.filter(
                        pk__in=OuterRef("id")
                    )
                )
            )
        else:
            qs = qs.annotate(is_following=Value(False, BooleanField()))

        qs = qs.annotate(
            item_count=Count(
                "taggit_taggeditem_items",
                filter=Q(
                    taggit_taggeditem_items__pk__in=self.get_tagged_items()
                ),
            )
        )

        return qs.order_by("-item_count", "name")


tag_list_view = TagListView.as_view()


class FollowingTagListView(LoginRequiredMixin, BaseTagListView):
    template_name = "activities/tags/following_tag_list.html"

    def get_queryset(self):
        return self.request.user.following_tags.order_by("name")


following_tag_list_view = FollowingTagListView.as_view()


class BlockedTagListView(LoginRequiredMixin, BaseTagListView):
    template_name = "activities/tags/blocked_tag_list.html"

    def get_queryset(self):
        return self.request.user.blocked_tags.order_by("name")


blocked_tag_list_view = BlockedTagListView.as_view()
