# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import BooleanField, Q, QuerySet, Value
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from django.views.generic import View
from rules.contrib.views import PermissionRequiredMixin
from vanilla import DeleteView, GenericModelView, ListView, UpdateView

from localhub.activities.views.streams import BaseStreamView
from localhub.comments.models import Comment
from localhub.comments.views import BaseCommentListView
from localhub.communities.models import Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.likes.models import Like
from localhub.private_messages.models import Message
from localhub.views import SearchMixin

from .forms import UserForm
from .notifications import send_user_notification


class BaseUserQuerySetMixin(CommunityRequiredMixin):
    def get_user_queryset(self):
        return get_user_model().objects.for_community(self.request.community)


class UserQuerySetMixin(BaseUserQuerySetMixin):
    def get_queryset(self):
        return self.get_user_queryset()


class CurrentUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(self):
        return self.request.user


class SingleUserMixin(BaseUserQuerySetMixin):

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.user_obj != self.request.user:
            self.user_obj.get_notifications().filter(
                recipient=self.request.user, is_read=False
            ).update(is_read=True)
        return response

    @cached_property
    def user_obj(self):
        return get_object_or_404(self.get_user_queryset(), username=self.kwargs["slug"])

    @cached_property
    def membership(self):
        return Membership.objects.filter(
            member=self.user_obj, community=self.request.community
        ).first()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "user_obj": self.user_obj,
                "is_current_user": self.user_obj == self.request.user,
                "membership": self.membership,
            }
        )
        return data


class BaseSingleUserView(UserQuerySetMixin, GenericModelView):
    lookup_field = "username"
    lookup_url_kwarg = "slug"


class BaseUserListView(UserQuerySetMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .order_by("name", "username")
            .exclude(blocked=self.request.user)
        )


class UserFollowView(PermissionRequiredMixin, BaseSingleUserView):
    permission_required = "users.follow_user"

    def post(self, request, *args, **kwargs):
        user = self.get_object()

        self.request.user.following.add(user)

        for notification in self.request.user.notify_on_follow(
            user, self.request.community
        ):
            send_user_notification(self.request.user, notification)

        return redirect(user)


user_follow_view = UserFollowView.as_view()


class UserUnfollowView(BaseSingleUserView):
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        self.request.user.following.remove(user)
        return redirect(user)


user_unfollow_view = UserUnfollowView.as_view()


class UserBlockView(PermissionRequiredMixin, BaseSingleUserView):
    permission_required = "users.block_user"

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        self.request.user.blocked.add(user)
        return redirect(user)


user_block_view = UserBlockView.as_view()


class UserUnblockView(BaseSingleUserView):
    def post(self, request, *args, **kwargs):
        user = self.get_object()
        self.request.user.blocked.remove(user)
        return redirect(user)


user_unblock_view = UserUnblockView.as_view()


class FollowingUserListView(BaseUserListView):
    template_name = "users/following_user_list.html"

    def get_queryset(self):
        return (
            self.request.user.following.annotate(
                is_following=Value(True, output_field=BooleanField())
            )
            .for_community(self.request.community)
            .order_by("name", "username")
        )


following_user_list_view = FollowingUserListView.as_view()


class FollowerUserListView(BaseUserListView):
    template_name = "users/follower_user_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(following=self.request.user)
            .with_is_following(self.request.user)
        )


follower_user_list_view = FollowerUserListView.as_view()


class BlockedUserListView(BaseUserListView):
    template_name = "users/blocked_user_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(blockers=self.request.user)
            .with_is_following(self.request.user)
        )


blocked_user_list_view = BlockedUserListView.as_view()


class UserAutocompleteListView(BaseUserListView):
    template_name = "users/user_autocomplete_list.html"

    def get_queryset(self):
        qs = super().get_queryset().exclude(blocked=self.request.user)
        search_term = self.request.GET.get("q", "").strip()
        if search_term:
            return qs.filter(
                Q(
                    Q(username__istartswith=search_term)
                    | Q(name__istartswith=search_term)
                )
            )[: settings.DEFAULT_PAGE_SIZE]
        return qs.none()


user_autocomplete_list_view = UserAutocompleteListView.as_view()


class MemberListView(SearchMixin, BaseUserListView):
    """
    Shows all members of community
    """

    template_name = "users/member_list.html"

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .exclude(blocked=self.request.user)
            .with_is_following(self.request.user)
        )
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


member_list_view = MemberListView.as_view()


class UserStreamView(SingleUserMixin, BaseStreamView):

    active_tab = "posts"
    template_name = "users/activities.html"

    def filter_queryset(self, queryset: QuerySet):
        return (
            super()
            .filter_queryset(queryset)
            .without_blocked_tags(self.request.user)
            .published()
            .filter(owner=self.user_obj)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(*self.models)
            .filter(recipient=self.user_obj, community=self.request.community)
            .count()
        )
        return data


user_stream_view = UserStreamView.as_view()


class UserCommentListView(SingleUserMixin, BaseCommentListView):
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


class UserCommentReplyListView(SingleUserMixin, BaseCommentListView):
    active_tab = "replies"
    template_name = "users/replies.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(parent__owner=self.user_obj)
            .order_by("-created")
        )


user_comment_reply_list_view = UserCommentReplyListView.as_view()


class UserMessageListView(SingleUserMixin, ListView):
    """
    Renders thread of all private messages between this user
    and the current user.
    """

    template_name = "users/messages.html"
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_user_queryset(self):
        return super().get_user_queryset().exclude(pk=self.request.user.id)

    def get_queryset(self):
        return (
            Message.objects.for_community(self.request.community)
            .between(self.request.user, self.user_obj)
            .with_sender_has_blocked(self.request.user)
            .select_related("sender", "recipient", "community")
            .order_by("-created")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        data.update(
            {
                "num_messages_sent": qs.filter(sender=self.request.user).count(),
                "num_messages_received": qs.filter(recipient=self.request.user).count(),
            }
        )
        return data


user_message_list_view = UserMessageListView.as_view()


class UserUpdateView(
    CurrentUserMixin, SuccessMessageMixin, PermissionRequiredMixin, UpdateView
):
    permission_required = "users.change_user"
    success_message = _("Your details have been updated")
    form_class = UserForm
    template_name = "users/user_form.html"

    def get_success_url(self):
        return self.request.path


user_update_view = UserUpdateView.as_view()


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()


class DarkmodeToggleView(View):
    def post(self, request):
        response = HttpResponse()

        if "darkmode" in request.COOKIES:
            response.delete_cookie("darkmode", domain=settings.SESSION_COOKIE_DOMAIN)
        else:
            response.set_cookie(
                "darkmode",
                "true",
                expires=datetime.datetime.now() + datetime.timedelta(days=365),
                domain=settings.SESSION_COOKIE_DOMAIN,
                httponly=True,
            )
        return response


darkmode_toggle_view = DarkmodeToggleView.as_view()
