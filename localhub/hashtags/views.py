# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import functools
import operator

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.db.models import BooleanField, Count, Exists, OuterRef, Q, Value
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _
from django.views.decorators.http import require_POST

# Third Party Libraries
from taggit.models import Tag, TaggedItem
from turbo_response import TurboFrame

# Localhub
from localhub.activities.utils import get_activity_models
from localhub.activities.views.streams import render_activity_stream
from localhub.common.pagination import render_paginated_queryset
from localhub.communities.decorators import community_required


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


@login_required
@community_required
def following_tag_list_view(request):
    return render_tag_list(
        request,
        request.user.following_tags.order_by("name"),
        "hashtags/list/following.html",
    )


@login_required
@community_required
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


@require_POST
@login_required
@community_required(permission="users.follow_tag")
def tag_follow_view(request, pk, remove=False):

    tag = get_object_or_404(Tag, pk=pk)

    if remove:
        request.user.following_tags.remove(tag)
        messages.info(request, _("You are no longer following #%(tag)s" % {"tag": tag}))
    else:
        request.user.following_tags.add(tag)
        messages.success(request, _("You are now following #%(tag)s" % {"tag": tag}))

    return (
        TurboFrame(f"hashtag-{tag.id}-follow")
        .template(
            "hashtags/includes/follow.html",
            {"object": tag, "is_following": not (remove)},
        )
        .response(request)
    )


@require_POST
@login_required
@community_required(permission="users.block_tag")
def tag_block_view(request, pk, remove=False):

    tag = get_object_or_404(Tag, pk=pk)

    if remove:
        request.user.blocked_tags.remove(tag)
        messages.info(request, _("You are no longer blocking #%(tag)s" % {"tag": tag}))
    else:
        request.user.blocked_tags.add(tag)
        messages.success(request, _("You are now blocking #%(tag)s" % {"tag": tag}))

    return (
        TurboFrame(f"hashtag-{tag.id}-block")
        .template(
            "hashtags/includes/block.html",
            {"object": tag, "is_blocked": not (remove)},
        )
        .response(request)
    )


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
