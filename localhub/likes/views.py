# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth.decorators import login_required

# Localhub
from localhub.activities.views.streams import render_activity_stream
from localhub.comments.views import get_comment_queryset
from localhub.common.pagination import render_paginated_queryset
from localhub.communities.decorators import community_required


@community_required
@login_required
def liked_stream_view(request):
    return render_activity_stream(
        request,
        lambda qs: qs.liked(request.user).with_liked_timestamp(request.user),
        "likes/activities.html",
        ordering=("-liked", "-created"),
    )


@community_required
@login_required
def liked_comment_list_view(request):
    comments = (
        get_comment_queryset(request)
        .liked(request.user)
        .with_common_annotations(request.user, request.community)
        .with_liked_timestamp(request.user)
        .order_by("-liked", "-created")
    )
    return render_paginated_queryset(request, comments, "likes/comments.html")
