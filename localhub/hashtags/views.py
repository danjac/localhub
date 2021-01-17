# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import functools
import operator

# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.generic import ListView

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin
from taggit.models import Tag, TaggedItem
from turbo_response import TurboFrame

# Localhub
from localhub.activities.utils import get_activity_models
from localhub.activities.views.streams import render_activity_stream
from localhub.common.pagination import render_paginated_queryset
from localhub.common.views import ActionView
from localhub.communities.decorators import community_required

# Local
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


def tag_autocomplete_list_view(request):
    if request.search:
        tags = get_tag_queryset(request, exclude_unused_tags=True).filter(
            name__istartswith=request.search
        )[: settings.DEFAULT_PAGE_SIZE]
    else:
        tags = Tag.objects.none()
    return TemplateResponse(
        request,
        "hashtags/list/autocomplete.html",
        {
            "object_list": tags,
            "content_warnings": request.community.get_content_warnings(),
        },
    )


@community_required
def tag_list_view(request):
    qs = get_tag_queryset(request, exclude_unused_tags=True)
    if request.search:
        qs = qs.filter(name__icontains=request.search)
    if request.user.is_authenticated:
        qs = qs.annotate(
            is_following=Exists(request.user.following_tags.filter(pk=OuterRef("id")))
        )
    else:
        qs = qs.annotate(is_following=Value(False, BooleanField()))

    qs = qs.annotate(
        item_count=Count(
            "taggit_taggeditem_items",
            filter=Q(taggit_taggeditem_items__pk__in=get_tagged_items(request)),
        )
    )

    qs = qs.order_by("-item_count", "name")

    return render_tag_list(request, qs, "hashtags/list/all.html")


@community_required
@login_required
def following_tag_list_view(request):
    return render_tag_list(
        request,
        request.user.following_tags.order_by("name"),
        "hashtags/list/following.html",
    )


@community_required
@login_required
def blocked_tag_list_view(request):
    return render_tag_list(
        request,
        request.user.blocked_tags.order_by("name"),
        "hashtags/list/blocked.html",
    )


@community_required
def tag_detail_view(request, slug):
    tag = get_object_or_404(Tag, slug=slug)

    def _filter_queryset(qs):
        qs = (
            qs.exclude_blocked_users(request.user)
            .published_or_owner(request.user)
            .filter(tags__name__in=[tag])
            .distinct()
        )
        # ensure we block all unwanted tags *unless* it's the tag
        # in question.
        if request.user.is_authenticated:
            qs = qs.exclude(
                Q(tags__in=request.user.blocked_tags.exclude(id=tag.id)),
                ~Q(owner=request.user),
            )
        return qs

    return render_activity_stream(
        request,
        _filter_queryset,
        "hashtags/tag_detail.html",
        extra_context={"tag": tag},
    )


class BaseTagActionView(PermissionRequiredMixin, TagQuerySetMixin, ActionView):
    def get_permission_object(self):
        return self.request.community


class BaseTagFollowView(BaseTagActionView):
    permission_required = "users.follow_tag"

    def render_to_response(self, is_following):
        return (
            TurboFrame(f"hashtag-{self.object.id}-follow")
            .template(
                "hashtags/includes/follow.html",
                {"object": self.object, "is_following": is_following},
            )
            .response(self.request)
        )


class TagFollowView(BaseTagFollowView):
    success_message = _("You are now following #%(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following_tags.add(self.object)
        return self.render_to_response(is_following=True)


tag_follow_view = TagFollowView.as_view()


class TagUnfollowView(BaseTagFollowView):
    success_message = _("You are no longer following #%(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following_tags.remove(self.object)
        return self.render_to_response(is_following=False)


tag_unfollow_view = TagUnfollowView.as_view()


class BaseTagBlockView(BaseTagActionView):
    permission_required = "users.block_tag"

    def render_to_response(self, is_blocked):
        return (
            TurboFrame(f"hashtag-{self.object.id}-block")
            .template(
                "hashtags/includes/block.html",
                {"object": self.object, "is_blocked": is_blocked},
            )
            .response(self.request)
        )


class TagBlockView(BaseTagBlockView):
    def post(self, request, *args, **kwargs):
        self.request.user.blocked_tags.add(self.object)
        return self.render_to_response(is_blocked=True)


tag_block_view = TagBlockView.as_view()


class TagUnblockView(BaseTagBlockView):
    success_message = _("You are no longer blocking #%(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.blocked_tags.remove(self.object)
        return self.render_to_response(is_blocked=False)


tag_unblock_view = TagUnblockView.as_view()


def get_tag_queryset(request, exclude_unused_tags=False):
    qs = Tag.objects.all()
    if exclude_unused_tags:
        qs = qs.filter(taggit_taggeditem_items__in=get_tagged_items(request))
    return qs.distinct()


def get_tagged_items(request):
    return TaggedItem.objects.filter(
        Q(
            functools.reduce(
                operator.or_,
                [
                    Q(
                        object_id__in=model.objects.filter(
                            community=request.community
                        ).values("id"),
                        content_type=content_type,
                    )
                    for model, content_type in ContentType.objects.get_for_models(
                        *get_activity_models()
                    ).items()
                ],
            )
        )
    )


def render_tag_list(request, tags, template_name):
    return render_paginated_queryset(
        request,
        tags,
        template_name,
        {"content_warnings": request.community.get_content_warnings()},
        page_size=settings.LONG_PAGE_SIZE,
    )
