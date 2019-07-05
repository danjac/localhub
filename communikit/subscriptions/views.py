# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import ListView

from taggit.models import Tag

from communikit.communities.views import CommunityRequiredMixin
from communikit.core.utils.content_types import get_generic_related_exists
from communikit.subscriptions.models import Subscription
from communikit.users.views import BaseUserListView


class SubscribedUserListView(LoginRequiredMixin, BaseUserListView):
    template_name = "subscriptions/user_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .filter(subscriptions__subscriber=self.request.user)
            .distinct()
        )


subscribed_user_list_view = SubscribedUserListView.as_view()


class SubscribedTagListView(
    CommunityRequiredMixin, LoginRequiredMixin, ListView
):
    template_name = "subscriptions/tag_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            Tag.objects.annotate(
                is_subscribed=get_generic_related_exists(
                    Tag,
                    Subscription.objects.filter(
                        subscriber=self.request.user,
                        community=self.request.community,
                    ),
                )
            )
            .filter(is_subscribed=True)
            .distinct()
            .order_by("name")
        )


subscribed_tag_list_view = SubscribedTagListView.as_view()
