# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

# Localhub
from localhub.activities.views.streams import render_activity_stream
from localhub.comments.models import Comment
from localhub.communities.decorators import community_required
from localhub.private_messages.models import Message


@community_required
@login_required
def bookmarks_stream_view(request):

    search = request.GET.get("q", None)

    def _filter_queryset(qs):
        qs = (
            qs.for_community(request.community)
            .published_or_owner(request.user)
            .bookmarked(request.user)
            .with_bookmarked_timestamp(request.user)
        )

        if search:
            qs = qs.search(qs)
        return qs

    return render_activity_stream(
        request,
        _filter_queryset,
        "bookmarks/activities.html",
        ordering=("-rank", "-bookmarked") if search else ("-bookmarked", "-created"),
        extra_context={"search": search},
    )


@community_required
@login_required
def bookmarks_message_list_view(request):
    messages = (
        Message.objects.for_community(request.community)
        .for_sender_or_recipient(request.user)
        .common_select_related()
        .bookmarked(request.user)
        .with_bookmarked_timestamp(request.user)
        .distinct()
    )

    if search := request.GET.get("q", None):
        messages = messages.search(search)
        ordering = ("-rank", "-bookmarked")
    else:
        ordering = ("-bookmarked", "-created")

    messages = messages.order_by(*ordering)

    return TemplateResponse(
        request,
        "bookmarks/messages.html",
        {"private_messages": messages, "search": search,},
    )


@community_required
@login_required
def bookmarks_comment_list_view(request):
    comments = (
        Comment.objects.for_community(request.community)
        .with_common_annotations(request.user, request.community)
        .exclude_blocked_users(request.user)
        .exclude_deleted()
        .with_common_related()
        .bookmarked(request.user)
        .with_bookmarked_timestamp(request.user)
    )
    if search := request.GET.get("q", None):
        comments = comments.search(search)
        ordering = ("-rank", "-bookmarked")
    else:
        ordering = ("-bookmarked", "-created")

    comments = comments.order_by(*ordering)

    return TemplateResponse(
        request, "bookmarks/comments.html", {"comments": comments, "search": search,},
    )
