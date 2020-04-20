# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.views.generic import ListView

from localhub.activities.utils import get_activity_models
from localhub.activities.views.streams import BaseActivityStreamView
from localhub.comments.models import Comment
from localhub.comments.views.list import BaseCommentListView
from localhub.likes.models import Like
from localhub.private_messages.models import Message

from .mixins import SingleUserMixin


class BaseUserActivityStreamView(SingleUserMixin, BaseActivityStreamView):
    ...


class BaseUserCommentListView(SingleUserMixin, BaseCommentListView):
    ...


class UserStreamView(BaseUserActivityStreamView):

    # do we need this tab?
    active_tab = "posts"
    template_name = "users/activities.html"

    def get_ordering(self):
        if self.is_current_user:
            return "-created"
        return "-published"

    def filter_queryset(self, queryset):
        qs = (
            super()
            .filter_queryset(queryset)
            .exclude_blocked_tags(self.request.user)
            .filter(owner=self.user_obj)
        )
        if self.is_current_user:
            return qs.published_or_owner(self.request.user)
        return qs.published()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(*get_activity_models())
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_stream_view = UserStreamView.as_view()


class UserCommentListView(BaseUserCommentListView):
    active_tab = "comments"
    template_name = "users/comments.html"

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.user_obj).order_by("-created")

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(Comment)
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_comment_list_view = UserCommentListView.as_view()


class UserMessageListView(SingleUserMixin, ListView):
    """
    Renders thread of all private messages between this user
    and the current user.
    """

    template_name = "users/messages.html"
    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE

    def get_queryset(self):
        if self.is_blocked:
            return Message.objects.none()
        qs = (
            Message.objects.for_community(self.request.community)
            .common_select_related()
            .order_by("-created")
            .distinct()
        )

        if self.is_current_user:
            qs = qs.for_sender_or_recipient(self.request.user)
        else:
            qs = qs.between(self.request.user, self.user_obj)
        return qs


user_message_list_view = UserMessageListView.as_view()


class UserActivityMentionsView(BaseUserActivityStreamView):
    """Activities where the user has an @mention (only
    published activities were user is not the owner)
    """

    template_name = "users/mentions/activities.html"

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .published()
            .exclude(owner=self.user_obj)
            .search(f"@{self.user_obj.username}")
        )


user_activity_mentions_view = UserActivityMentionsView.as_view()


class UserCommentMentionsView(BaseUserCommentListView):

    template_name = "users/mentions/comments.html"

    def get_queryset(self, queryset):
        return (
            super()
            .get_queryset()
            .exclude(owner=self.user_obj)
            .search(f"@{self.user_obj.username}")
            .order_by("-created")
        )


user_comment_mentions_view = UserCommentMentionsView.as_view()
