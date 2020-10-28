# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.template.response import TemplateResponse
from django.utils.functional import cached_property

# Localhub
from localhub.common.mixins import ParentObjectMixin
from localhub.communities.mixins import CommunityRequiredMixin
from localhub.communities.models import Membership
from localhub.private_messages.models import Message


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
    parent_context_object_name = "user_obj"
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
        if request.user.is_authenticated and self.user_obj != request.user:
            self.user_obj.get_notifications().for_recipient(request.user).mark_read()
        return response

    @cached_property
    def user_obj(self):
        return self.get_parent_object()

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
        if self.request.user.is_anonymous:
            return False
        return (
            not self.is_current_user
            and self.user_obj in self.request.user.following.all()
        )

    @cached_property
    def is_follower(self):
        if self.request.user.is_anonymous:
            return False
        return (
            not self.is_current_user
            and self.request.user in self.user_obj.following.all()
        )

    @cached_property
    def is_blocker(self):
        if self.is_current_user or self.request.user.is_anonymous:
            return False
        return self.request.user.blockers.filter(pk=self.user_obj.id).exists()

    @cached_property
    def is_blocking(self):
        if self.is_current_user or self.request.user.is_anonymous:
            return False
        return self.request.user.blocked.filter(pk=self.user_obj.id).exists()

    @cached_property
    def unread_messages(self):
        if self.is_current_user or self.request.user.is_anonymous:
            return 0

        return (
            Message.objects.for_community(self.request.community)
            .from_sender_to_recipient(self.user_obj, self.request.user)
            .unread()
            .count()
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            **{
                "is_current_user": self.is_current_user,
                "is_blocked": self.is_blocked,
                "is_blocker": self.is_blocker,
                "is_blocking": self.is_blocking,
                "is_following": self.is_following,
                "is_follower": self.is_follower,
                "display_name": self.display_name,
                "membership": self.membership,
                "unread_messages": self.unread_messages,
            },
        }
