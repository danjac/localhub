# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib.auth.decorators import login_required
from django.template.response import TemplateResponse

# Localhub
from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.views import get_comment_queryset
from localhub.communities.decorators import community_required


class LikedStreamView(BaseActivityStreamView):
    template_name = "likes/activities.html"
    ordering = ("-liked", "-created")

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(model.objects.liked(self.request.user))

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .liked(self.request.user)
            .with_liked_timestamp(self.request.user)
        )


liked_stream_view = LikedStreamView.as_view()


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
    return TemplateResponse(request, "likes/comments.html", {"comments": comments})
