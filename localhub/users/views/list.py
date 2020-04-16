# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db.models import Q
from vanilla import ListView

from localhub.views import SearchMixin

from .mixins import UserQuerySetMixin


class BaseUserListView(UserQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE

    exclude_blocked = True

    include_is_following = True
    include_membership_details = True
    include_unread_messages = True

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .exclude(blocked=self.request.user)
            .order_by("name", "username")
        )

        if self.exclude_blocked:
            qs = qs.exclude(blockers=self.request.user)

        if self.include_is_following:
            qs = qs.with_is_following(self.request.user)

        if self.include_membership_details:
            qs = qs.with_role(self.request.community).with_joined(
                self.request.community
            )

        if self.include_unread_messages:
            qs = qs.with_num_unread_messages(self.request.user, self.request.community)

        return qs


class MemberListView(SearchMixin, BaseUserListView):
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


class FollowingUserListView(BaseUserListView):
    template_name = "users/following_user_list.html"

    def get_queryset(self):
        return super().get_queryset().filter(followers=self.request.user)


following_user_list_view = FollowingUserListView.as_view()


class FollowerUserListView(BaseUserListView):
    template_name = "users/follower_user_list.html"

    def get_queryset(self):
        return super().get_queryset().filter(following=self.request.user)


follower_user_list_view = FollowerUserListView.as_view()


class BlockedUserListView(BaseUserListView):
    template_name = "users/blocked_user_list.html"

    exclude_blocked = False

    include_is_following = False
    include_unread_messages = False

    def get_queryset(self):
        return super().get_queryset().filter(blockers=self.request.user)


blocked_user_list_view = BlockedUserListView.as_view()


class UserAutocompleteListView(BaseUserListView):
    template_name = "users/user_autocomplete_list.html"

    include_is_following = False
    include_unread_messages = False
    include_membership_details = False

    def get_queryset(self):
        qs = super().get_queryset()
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
