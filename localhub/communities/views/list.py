# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, F, Q
from django.views.generic import ListView

from localhub.join_requests.models import JoinRequest
from localhub.views import SearchMixin

from ..models import Community, Membership
from .mixins import CommunityAdminRequiredMixin, MembershipQuerySetMixin


class CommunityListView(LoginRequiredMixin, SearchMixin, ListView):
    """
    Returns all public communities, or communities the
    current user belongs to.

    TBD: list invites (matching email)
    """

    paginate_by = settings.LOCALHUB_DEFAULT_PAGE_SIZE
    template_name = "communities/community_list.html"

    def get_queryset(self):
        qs = Community.objects.accessible(self.request.user).order_by("name")
        if self.search_query:
            qs = qs.filter(name__icontains=self.search_query)
        return qs

    def get_member_communities(self):
        return Community.objects.filter(
            membership__member=self.request.user, membership__active=True
        ).exclude(pk=self.request.community.id)

    def get_available_users(self):
        return (
            get_user_model()
            .objects.filter(is_active=True)
            .exclude(pk__in=self.request.user.blocked.all())
        )

    def get_notifications_count(self):
        return dict(
            self.get_member_communities()
            .annotate(
                num_notifications=Count(
                    "notification",
                    filter=Q(
                        notification__recipient=self.request.user,
                        notification__is_read=False,
                        notification__actor__pk__in=self.get_available_users(),
                        notification__actor__membership__active=True,
                        notification__actor__membership__community=F("pk"),
                    ),
                    distinct=True,
                )
            )
            .values_list("id", "num_notifications")
        )

    def get_flags_count(self):
        return dict(
            self.get_member_communities()
            .filter(
                membership__role__in=(Membership.Role.ADMIN, Membership.Role.MODERATOR,)
            )
            .annotate(num_flags=Count("flag", distinct=True))
            .values_list("id", "num_flags")
        )

    def get_messages_count(self):
        return dict(
            self.get_member_communities()
            .annotate(
                num_messages=Count(
                    "message",
                    filter=Q(
                        message__recipient=self.request.user,
                        message__read__isnull=True,
                        message__sender__pk__in=self.get_available_users(),
                        message__sender__membership__active=True,
                        message__sender__membership__community=F("pk"),
                    ),
                    distinct=True,
                )
            )
            .values_list("id", "num_messages")
        )

    def get_join_requests_count(self):
        return dict(
            self.get_member_communities()
            .filter(membership__role=Membership.Role.ADMIN)
            .annotate(
                num_join_requests=Count(
                    "joinrequest",
                    filter=Q(joinrequest__status=JoinRequest.Status.PENDING),
                    distinct=True,
                )
            )
            .values_list("id", "num_join_requests")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "counters": {
                    "flags": self.get_flags_count(),
                    "join_requests": self.get_join_requests_count(),
                    "messages": self.get_messages_count(),
                    "notifications": self.get_notifications_count(),
                },
                "roles": dict(Membership.Role.choices),
            }
        )
        return data


community_list_view = CommunityListView.as_view()


class MembershipListView(
    CommunityAdminRequiredMixin, MembershipQuerySetMixin, SearchMixin, ListView,
):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE
    model = Membership

    def get_queryset(self):
        qs = super().get_queryset().order_by("member__name", "member__username")

        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


membership_list_view = MembershipListView.as_view()
