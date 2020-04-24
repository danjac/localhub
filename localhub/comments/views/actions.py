# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import IntegrityError
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.bookmarks.models import Bookmark
from localhub.likes.models import Like
from localhub.views import SuccessActionView, SuccessDeleteView

from .mixins import CommentQuerySetMixin


class BaseCommentActionView(CommentQuerySetMixin, SuccessActionView):
    ...


class BaseCommentBookmarkView(PermissionRequiredMixin, BaseCommentActionView):
    permission_required = "comments.bookmark_comment"
    is_success_ajax_response = True


class CommentBookmarkView(BaseCommentBookmarkView):
    success_message = _("You have bookmarked this comment")

    def post(self, request, *args, **kwargs):
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            pass
        return self.success_response()


comment_bookmark_view = CommentBookmarkView.as_view()


class CommentRemoveBookmarkView(BaseCommentBookmarkView):
    success_message = _("You have removed this comment from your bookmarks")

    def post(self, request, *args, **kwargs):
        Bookmark.objects.filter(user=request.user, comment=self.object).delete()
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


comment_remove_bookmark_view = CommentRemoveBookmarkView.as_view()


class BaseCommentLikeView(PermissionRequiredMixin, BaseCommentActionView):
    permission_required = "comments.like_comment"
    is_success_ajax_response = True


class CommentLikeView(BaseCommentLikeView):
    success_message = _("You have liked this comment")

    def post(self, request, *args, **kwargs):
        try:
            Like.objects.create(
                user=request.user,
                community=request.community,
                recipient=self.object.owner,
                content_object=self.object,
            ).notify()
        except IntegrityError:
            pass
        return self.success_response()


comment_like_view = CommentLikeView.as_view()


class CommentDislikeView(BaseCommentLikeView):
    success_message = _("You have stopped liking this comment")

    def post(self, request, *args, **kwargs):
        Like.objects.filter(user=request.user, comment=self.object).delete()
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


comment_dislike_view = CommentDislikeView.as_view()


class CommentDeleteView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessDeleteView,
):
    permission_required = "comments.delete_comment"
    template_name = "comments/comment_confirm_delete.html"
    success_message = _("You have deleted this comment")

    def get_success_url(self):
        obj = self.object.get_content_object()
        if obj:
            return obj.get_absolute_url()
        return reverse("comments:list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        return self.success_response()


comment_delete_view = CommentDeleteView.as_view()
