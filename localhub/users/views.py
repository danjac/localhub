# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from typing import Optional

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import BooleanField, Q, QuerySet, Value
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)
from django.views.generic.base import ContextMixin
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.activities.views.streams import BaseStreamView
from localhub.comments.models import Comment
from localhub.comments.views import CommentListView
from localhub.communities.models import Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.core.types import ContextDict
from localhub.likes.models import Like
from localhub.private_messages.models import Message
from localhub.users.emails import send_user_notification_email
from localhub.users.forms import UserForm


class AuthenticatedUserMixin(LoginRequiredMixin):
    """
    Always returns the current logged in user.
    """

    def get_object(
        self, queryset: Optional[QuerySet] = None
    ) -> settings.AUTH_USER_MODEL:
        return self.request.user


class UserUpdateView(
    AuthenticatedUserMixin,
    SuccessMessageMixin,
    PermissionRequiredMixin,
    UpdateView,
):
    permission_required = "users.change_user"
    success_message = _("Your details have been updated")
    form_class = UserForm

    def get_success_url(self) -> str:
        return self.request.path


user_update_view = UserUpdateView.as_view()


class UserDeleteView(
    AuthenticatedUserMixin, PermissionRequiredMixin, DeleteView
):
    permission_required = "users.delete_user"
    success_url = settings.HOME_PAGE_URL


user_delete_view = UserDeleteView.as_view()


class UserSlugMixin:
    slug_field = "username"


class UserContextMixin(ContextMixin):
    context_object_name = "user_obj"

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["is_auth_user"] = self.request.user == self.object
        try:
            data["membership"] = Membership.objects.get(
                member=self.object, community=self.request.community
            )
        except Membership.DoesNotExist:
            pass  # shouldn't happen, but just in case
        return data


class UserQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return get_user_model().objects.active(self.request.community)


class UserDetailView(
    UserSlugMixin, UserContextMixin, UserQuerySetMixin, DetailView
):
    ...


user_detail_view = UserDetailView.as_view()


class SingleUserView(
    UserSlugMixin, UserQuerySetMixin, SingleObjectMixin, View
):
    ...


class UserFollowView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleUserView
):
    permission_required = "users.follow_user"

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        self.request.user.following.add(self.object)

        for notification in self.request.user.notify_on_follow(
            self.object, self.request.community
        ):
            send_user_notification_email(self.request.user, notification)

        return HttpResponseRedirect(self.get_success_url())


user_follow_view = UserFollowView.as_view()


class UserUnfollowView(LoginRequiredMixin, SingleUserView):
    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.request.user.following.remove(self.object)
        return HttpResponseRedirect(self.get_success_url())


user_unfollow_view = UserUnfollowView.as_view()


class UserBlockView(
    LoginRequiredMixin, PermissionRequiredMixin, SingleUserView
):
    permission_required = "users.block_user"

    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()

        self.request.user.blocked.add(self.object)
        return HttpResponseRedirect(self.get_success_url())


user_block_view = UserBlockView.as_view()


class UserUnblockView(LoginRequiredMixin, SingleUserView):
    def get_success_url(self) -> str:
        return self.object.get_absolute_url()

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.request.user.blocked.remove(self.object)
        return HttpResponseRedirect(self.get_success_url())


user_unblock_view = UserUnblockView.as_view()


class BaseUserListView(UserQuerySetMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("name", "username")


class FollowingUserListView(LoginRequiredMixin, BaseUserListView):
    template_name = "users/following_user_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            self.request.user.following.annotate(
                is_following=Value(True, output_field=BooleanField())
            )
            .active(self.request.community)
            .order_by("name", "username")
        )


following_user_list_view = FollowingUserListView.as_view()


class FollowerUserListView(LoginRequiredMixin, BaseUserListView):
    template_name = "users/follower_user_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(following=self.request.user)
            .with_is_following(self.request.user)
        )


follower_user_list_view = FollowerUserListView.as_view()


class BlockedUserListView(LoginRequiredMixin, BaseUserListView):
    template_name = "users/blocked_user_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(blockers=self.request.user)
            .with_is_following(self.request.user)
        )


blocked_user_list_view = BlockedUserListView.as_view()


class UserAutocompleteListView(LoginRequiredMixin, BaseUserListView):
    template_name = "users/user_autocomplete_list.html"

    def get_queryset(self) -> QuerySet:
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


class SingleUserMixin(
    CommunityRequiredMixin, UserSlugMixin, UserContextMixin, SingleObjectMixin
):
    """
    Used to mix with views using non-user querysets
    """

    def get(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object(
            queryset=get_user_model().objects.active(self.request.community)
        )
        return super().get(request, *args, **kwargs)


class UserStreamView(SingleUserMixin, BaseStreamView):

    active_tab = "posts"
    template_name = "users/activities.html"

    def filter_queryset(self, queryset: QuerySet) -> QuerySet:
        return (
            super()
            .filter_queryset(queryset)
            .blocked_tags(self.request.user)
            .filter(owner=self.object)
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(*self.models)
            .filter(recipient=self.object, community=self.request.community)
            .count()
        )
        return data


user_stream_view = UserStreamView.as_view()


class UserCommentListView(SingleUserMixin, CommentListView):
    active_tab = "comments"
    template_name = "users/comments.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(owner=self.object)
            .with_common_annotations(self.request.community, self.request.user)
            .order_by("-created")
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["num_likes"] = (
            Like.objects.for_models(Comment)
            .filter(recipient=self.object, community=self.request.community)
            .count()
        )
        return data


user_comment_list_view = UserCommentListView.as_view()


class UserMessageListView(LoginRequiredMixin, SingleUserMixin, ListView):
    """
    Renders thread of all private messages between this user
    and the current user.
    """

    template_name = "users/messages.html"

    def get_user_queryset(self) -> QuerySet:
        return super().get_user_queryset().exclude(pk=self.request.user.id)

    def get_queryset(self) -> QuerySet:
        return (
            Message.objects.with_num_replies()
            .filter(
                Q(Q(recipient=self.object) | Q(sender=self.object))
                & Q(
                    Q(recipient=self.request.user)
                    | Q(sender=self.request.user)
                ),
                community=self.request.community,
            )
            .select_related("sender", "recipient", "parent", "community")
            .order_by("-created")
            .distinct()
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        data.update(
            {
                "num_messages_sent": qs.filter(
                    sender=self.request.user
                ).count(),
                "num_messages_received": qs.filter(
                    recipient=self.request.user
                ).count(),
            }
        )
        return data


user_message_list_view = UserMessageListView.as_view()
