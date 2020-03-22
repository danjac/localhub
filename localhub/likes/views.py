# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext as _

from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.views import BaseCommentListView
from localhub.views import PageTitleMixin


class LikedPageTitleMixin(PageTitleMixin):
    def get_page_title_segments(self):
        return [_("Favorites")]


class LikedStreamView(LikedPageTitleMixin, BaseActivityStreamView):
    template_name = "likes/activities.html"

    def get_page_title_segments(self):
        return super().get_page_title_segments() + [_("Activities")]

    def get_count_queryset_for_model(self, model):
        return self.filter_queryset(model.objects.with_has_liked(self.request.user))

    def filter_queryset(self, queryset):
        return super().filter_queryset(queryset).filter(has_liked=True)


liked_stream_view = LikedStreamView.as_view()


class LikedCommentListView(LikedPageTitleMixin, BaseCommentListView):
    template_name = "likes/comments.html"

    def get_page_title_segments(self):
        return super().get_page_title_segments() + [_("Comments")]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_common_annotations(self.request.user, self.request.community)
            .filter(has_liked=True)
            .order_by("-created")
        )


liked_comment_list_view = LikedCommentListView.as_view()
