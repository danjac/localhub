# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import DeleteView, ListView, View

from rules.contrib.views import PermissionRequiredMixin

from localhub.apps.activities.utils import get_activity_models
from localhub.apps.activities.views.streams import BaseActivityStreamView
from localhub.apps.comments.models import Comment
from localhub.apps.comments.views import BaseCommentListView
from localhub.apps.communities.models import Membership
from localhub.apps.communities.views import CommunityRequiredMixin
from localhub.apps.likes.models import Like
from localhub.apps.private_messages.models import Message
from localhub.common.views import (
    ParentObjectMixin,
    SearchMixin,
    SuccessActionView,
    SuccessUpdateView,
)

from .forms import UserForm


class BaseUserQuerySetMixin(CommunityRequiredMixin):

    # users blocking me
    exclude_blocker_users = True

    # users I am blocking
    exclude_blocked_users = False

    # users blocking me, or whom I am blocking
    exclude_blocking_users = False

    def get_user_queryset(self):
        qs = get_user_model().objects.for_community(self.request.community)

        if self.exclude_blocking_users:
            qs = qs.exclude_blocking(self.request.user)

        elif self.exclude_blocked_users:
            qs = qs.exclude_blocked(self.request.user)

        elif self.exclude_blocker_users:
            qs = qs.exclude_blockers(self.request.user)

        return qs


class UserQuerySetMixin(BaseUserQuerySetMixin):
    def get_queryset(self):
        return self.get_user_queryset()


class MemberQuerySetMixin:
    """Includes membership details such as role and join date"""

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_role(self.request.community)
            .with_joined(self.request.community)
        )


class CurrentUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(self):
        return self.request.user


class SingleUserMixin(ParentObjectMixin, BaseUserQuerySetMixin):
    parent_slug_kwarg = "username"
    parent_slug_field = "username"
    parent_object_name = "user_obj"
    parent_required = False

    def get_parent_queryset(self):
        return self.get_user_queryset()

    def get(self, request, *args, **kwargs):
        if self.user_obj is None:
            return TemplateResponse(
                request,
                "users/detail/not_found.html",
                {"username": kwargs["username"]},
                status=404,
            )
        response = super().get(request, *args, **kwargs)
        if self.user_obj != request.user:
            self.user_obj.get_notifications().for_recipient(request.user).mark_read()
        return response

    @cached_property
    def display_name(self):
        return self.user_obj.get_display_name()

    @cached_property
    def membership(self):
        return Membership.objects.filter(
            member=self.user_obj, community=self.request.community
        ).first()

    @cached_property
    def is_current_user(self):
        return self.user_obj == self.request.user

    @cached_property
    def is_blocked(self):
        return self.is_blocker or self.is_blocking

    @cached_property
    def is_following(self):
        return (
            not self.is_current_user
            and self.user_obj in self.request.user.following.all()
        )

    @cached_property
    def is_follower(self):
        return (
            not self.is_current_user
            and self.request.user in self.user_obj.following.all()
        )

    @cached_property
    def is_blocker(self):
        if self.is_current_user:
            return False
        return self.request.user.blockers.filter(pk=self.user_obj.id).exists()

    @cached_property
    def is_blocking(self):
        if self.is_current_user:
            return False
        return self.request.user.blocked.filter(pk=self.user_obj.id).exists()

    @cached_property
    def unread_messages(self):
        if self.is_current_user:
            return 0

        return (
            Message.objects.from_sender_to_recipient(self.user_obj, self.request.user)
            .unread()
            .count()
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "is_current_user": self.is_current_user,
                "is_blocked": self.is_blocked,
                "is_blocker": self.is_blocker,
                "is_blocking": self.is_blocking,
                "is_following": self.is_following,
                "is_follower": self.is_follower,
                "display_name": self.display_name,
                "membership": self.membership,
                "unread_messages": self.unread_messages,
            }
        )
        return data


class BaseUserActivityStreamView(SingleUserMixin, BaseActivityStreamView):
    ...


class BaseUserCommentListView(SingleUserMixin, BaseCommentListView):
    ...


class UserStreamView(BaseUserActivityStreamView):

    template_name = "users/detail/activities.html"

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
    template_name = "users/detail/comments.html"

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

    template_name = "users/detail/messages.html"
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


class UserActivityLikesView(BaseUserActivityStreamView):
    """Liked activities published by this user."""

    template_name = "users/likes/activities.html"
    ordering = ("-num_likes", "-published")

    exclude_blocking_users = True

    def filter_queryset(self, queryset):
        return (
            super()
            .filter_queryset(queryset)
            .with_num_likes()
            .published()
            .filter(owner=self.user_obj, num_likes__gt=0)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(*get_activity_models())
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_activity_likes_view = UserActivityLikesView.as_view()


class UserCommentLikesView(BaseUserCommentListView):
    """Liked comments submitted by this user."""

    template_name = "users/likes/comments.html"

    exclude_blocking_users = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(owner=self.user_obj, num_likes__gt=0)
            .order_by("-num_likes", "-created")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(Comment)
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_comment_likes_view = UserCommentLikesView.as_view()


class UserActivityMentionsView(BaseUserActivityStreamView):
    """Activities where the user has an @mention (only
    published activities were user is not the owner)
    """

    template_name = "users/mentions/activities.html"

    exclude_blocking_users = True

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

    exclude_blocking_users = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude(owner=self.user_obj)
            .search(f"@{self.user_obj.username}")
            .order_by("-created")
        )


user_comment_mentions_view = UserCommentMentionsView.as_view()


class BaseUserListView(UserQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE

    def get_queryset(self):
        return super().get_queryset().order_by("name", "username")


class BaseMemberListView(MemberQuerySetMixin, BaseUserListView):

    exclude_blocking_users = True

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_is_following(self.request.user)
            .with_num_unread_messages(self.request.user, self.request.community)
        )


class MemberListView(SearchMixin, BaseMemberListView):
    """
    Shows all members of community
    """

    template_name = "users/list/members.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


member_list_view = MemberListView.as_view()


class FollowingUserListView(BaseMemberListView):
    template_name = "users/list/following.html"

    def get_queryset(self):
        return super().get_queryset().filter(followers=self.request.user)


following_user_list_view = FollowingUserListView.as_view()


class FollowerUserListView(BaseMemberListView):
    template_name = "users/list/followers.html"

    def get_queryset(self):
        return super().get_queryset().filter(following=self.request.user)


follower_user_list_view = FollowerUserListView.as_view()


class BlockedUserListView(MemberQuerySetMixin, BaseUserListView):
    template_name = "users/list/blocked.html"

    def get_queryset(self):
        return super().get_queryset().filter(blockers=self.request.user)


blocked_user_list_view = BlockedUserListView.as_view()


class UserAutocompleteListView(BaseUserListView):
    template_name = "users/list/autocomplete.html"

    exclude_blocking_users = True

    def get_queryset(self):
        # exclude current user by default
        qs = super().get_queryset().exclude(pk=self.request.user.pk)
        search_term = self.request.GET.get("q", "").strip()
        if search_term:
            return qs.filter(
                Q(
                    Q(username__istartswith=search_term)
                    | Q(name__istartswith=search_term)
                )
            )[: settings.LOCALHUB_DEFAULT_PAGE_SIZE]
        return qs.none()


user_autocomplete_list_view = UserAutocompleteListView.as_view()


class UserUpdateView(
    CurrentUserMixin, PermissionRequiredMixin, SuccessUpdateView,
):
    permission_required = "users.change_user"
    success_message = _("Your details have been updated")
    form_class = UserForm
    template_name = "users/user_form.html"
    is_multipart = True

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        self.object = form.save()
        self.object.notify_on_update()
        return self.success_response()


user_update_view = UserUpdateView.as_view()


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()


class BaseUserActionView(UserQuerySetMixin, SuccessActionView):
    slug_field = "username"
    slug_url_kwarg = "username"


class BaseFollowUserView(
    PermissionRequiredMixin, BaseUserActionView,
):
    permission_required = "users.follow_user"
    is_success_ajax_response = True
    exclude_blocking_users = True


class UserFollowView(BaseFollowUserView):
    success_message = _("You are now following %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following.add(self.object)
        self.request.user.notify_on_follow(self.object, self.request.community)

        return self.success_response()


user_follow_view = UserFollowView.as_view()


class UserUnfollowView(BaseFollowUserView):
    success_message = _("You are no longer following %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.following.remove(self.object)
        return self.success_response()


user_unfollow_view = UserUnfollowView.as_view()


class BaseUserBlockView(PermissionRequiredMixin, BaseUserActionView):
    permission_required = "users.block_user"


class UserBlockView(BaseUserBlockView):
    success_message = _("You are now blocking %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.block_user(self.object)
        return self.success_response()


user_block_view = UserBlockView.as_view()


class UserUnblockView(BaseUserBlockView):
    success_message = _("You are no longer blocking %(object)s")

    def post(self, request, *args, **kwargs):
        self.request.user.blocked.remove(self.object)
        return self.success_response()


user_unblock_view = UserUnblockView.as_view()


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()


class DismissNoticeView(CurrentUserMixin, View):
    def post(self, request, notice):
        self.request.user.dismiss_notice(notice)
        return HttpResponse()


dismiss_notice_view = DismissNoticeView.as_view()
