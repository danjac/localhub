# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.db.models import BooleanField, Q, Value
from vanilla import ListView

from localhub.views import SearchMixin

from .mixins import UserQuerySetMixin


class BaseUserListView(UserQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .with_role(self.request.community)
            .order_by("name", "username")
            .exclude(blocked=self.request.user)
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["blocked_users"] = self.request.user.get_blocked_users()
        return data


class FollowingUserListView(BaseUserListView):
    template_name = "users/following_user_list.html"

    def get_queryset(self):
        return (
            self.request.user.following.annotate(
                is_following=Value(True, output_field=BooleanField())
            )
            .for_community(self.request.community)
            .with_role(self.request.community)
            .with_num_unread_messages(self.request.user, self.request.community)
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
            .for_community(self.request.community)
            .with_role(self.request.community)
            .with_is_following(self.request.user)
            .with_num_unread_messages(self.request.user, self.request.community)
        )


follower_user_list_view = FollowerUserListView.as_view()


class BlockedUserListView(BaseUserListView):
    template_name = "users/blocked_user_list.html"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(blockers=self.request.user)
            .for_community(self.request.community)
            .with_role(self.request.community)
            .with_is_following(self.request.user)
        )


blocked_user_list_view = BlockedUserListView.as_view()


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
            .for_community(self.request.community)
            .with_role(self.request.community)
            .with_is_following(self.request.user)
            .with_num_unread_messages(self.request.user, self.request.community)
        )
        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


member_list_view = MemberListView.as_view()


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
            )[: settings.LOCALHUB_DEFAULT_PAGE_SIZE]
        return qs.none()


user_autocomplete_list_view = UserAutocompleteListView.as_view()
