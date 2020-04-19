# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.utils.functional import cached_property

from localhub.communities.models import Membership
from localhub.communities.views import CommunityRequiredMixin
from localhub.private_messages.models import Message


class BaseUserQuerySetMixin(CommunityRequiredMixin):
    def get_user_queryset(self):
        return get_user_model().objects.for_community(self.request.community)


class UserQuerySetMixin(BaseUserQuerySetMixin):
    def get_queryset(self):
        return self.get_user_queryset()


class ExcludeBlockersQuerySetMixin:
    """Excludes any users blocking the current user"""

    def get_queryset(self):
        return super().get_queryset().exclude_blockers(self.request.user)


class ExcludeBlockedQuerySetMixin:
    """Excludes any users blocked by the current user"""

    def get_queryset(self):
        return super().get_queryset().exclude_blocked(self.request.user)


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


class SingleUserMixin(BaseUserQuerySetMixin):
    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        if self.user_obj != self.request.user:
            self.user_obj.get_notifications().for_recipient(
                self.request.user
            ).mark_read()
        return response

    @cached_property
    def user_obj(self):
        return get_object_or_404(
            self.get_user_queryset(), username=self.kwargs["username"]
        )

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
                "user_obj": self.user_obj,
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
