# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db.models import Q
from django.views.generic import ListView

from localhub.views import SearchMixin

from .mixins import (
    ExcludeBlockedQuerySetMixin,
    ExcludeBlockersQuerySetMixin,
    MemberQuerySetMixin,
    UserQuerySetMixin,
)


class BaseUserListView(ExcludeBlockersQuerySetMixin, UserQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE

    def get_queryset(self):
        return super().get_queryset().order_by("name", "username")


class BaseMemberListView(
    MemberQuerySetMixin, ExcludeBlockedQuerySetMixin, BaseUserListView
):
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

    template_name = "users/member_list.html"

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


member_list_view = MemberListView.as_view()


class FollowingUserListView(BaseMemberListView):
    template_name = "users/following_user_list.html"

    def get_queryset(self):
        return super().get_queryset().filter(followers=self.request.user)


following_user_list_view = FollowingUserListView.as_view()


class FollowerUserListView(BaseMemberListView):
    template_name = "users/follower_user_list.html"

    def get_queryset(self):
        return super().get_queryset().filter(following=self.request.user)


follower_user_list_view = FollowerUserListView.as_view()


class BlockedUserListView(MemberQuerySetMixin, BaseUserListView):
    template_name = "users/blocked_user_list.html"

    def get_queryset(self):
        return super().get_queryset().filter(blockers=self.request.user)


blocked_user_list_view = BlockedUserListView.as_view()


class UserAutocompleteListView(ExcludeBlockedQuerySetMixin, BaseUserListView):
    template_name = "users/user_autocomplete_list.html"

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
