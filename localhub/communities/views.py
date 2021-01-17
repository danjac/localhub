# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.db.models import Count, F, Q
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _
from django.views.generic import DeleteView, DetailView, ListView, TemplateView

# Third Party Libraries
import rules
from rules.contrib.views import PermissionRequiredMixin
from turbo_response.views import TurboUpdateView

# Localhub
from localhub.common.mixins import SearchMixin
from localhub.common.pagination import render_paginated_queryset
from localhub.invites.models import Invite
from localhub.join_requests.models import JoinRequest

# Local
from .decorators import community_required
from .emails import send_membership_deleted_email
from .forms import CommunityForm, MembershipForm
from .mixins import (
    CommunityAdminRequiredMixin,
    CurrentCommunityMixin,
    MembershipQuerySetMixin,
)
from .models import Community, Membership


@community_required
def community_list_view(request):
    qs = Community.objects.accessible(request.user).order_by("name")
    if request.search:
        qs = qs.filter(name__icontains=request.search)

    if request.user.is_authenticated:

        communities = Community.objects.filter(
            membership__member=request.user, membership__active=True
        ).exclude(pk=request.community.id)

        users = (
            get_user_model()
            .objects.filter(is_active=True)
            .exclude(pk__in=request.user.blocked.all())
        )

        flags = dict(
            communities.filter(
                membership__role__in=(
                    Membership.Role.ADMIN,
                    Membership.Role.MODERATOR,
                )
            )
            .annotate(num_flags=Count("flag", distinct=True))
            .values_list("id", "num_flags")
        )
        join_requests = dict(
            communities.filter(membership__role=Membership.Role.ADMIN)
            .annotate(
                num_join_requests=Count(
                    "joinrequest",
                    filter=Q(joinrequest__status=JoinRequest.Status.PENDING),
                    distinct=True,
                )
            )
            .values_list("id", "num_join_requests")
        )
        messages = dict(
            communities.annotate(
                num_messages=Count(
                    "message",
                    filter=Q(
                        message__recipient=request.user,
                        message__read__isnull=True,
                        message__sender__pk__in=users,
                        message__sender__membership__active=True,
                        message__sender__membership__community=F("pk"),
                    ),
                    distinct=True,
                )
            ).values_list("id", "num_messages")
        )
        notifications = dict(
            communities.annotate(
                num_notifications=Count(
                    "notification",
                    filter=Q(
                        notification__recipient=request.user,
                        notification__is_read=False,
                        notification__actor__pk__in=users,
                        notification__actor__membership__active=True,
                        notification__actor__membership__community=F("pk"),
                    ),
                    distinct=True,
                )
            ).values_list("id", "num_notifications")
        )

    else:
        flags = {}
        join_requests = {}
        messages = {}
        notifications = {}

    return render_paginated_queryset(
        request,
        qs,
        "communities/community_list.html",
        {
            "counters": {
                "flags": flags,
                "join_requests": join_requests,
                "messages": messages,
                "notifications": notifications,
            },
            "roles": dict(Membership.Role.choices),
        },
    )


class CommunityUpdateView(
    SuccessMessageMixin,
    CurrentCommunityMixin,
    CommunityAdminRequiredMixin,
    TurboUpdateView,
):
    form_class = CommunityForm
    success_message = _("Community settings have been updated")

    def get_success_url(self):
        return self.request.path


community_update_view = CommunityUpdateView.as_view()


class BaseCommunityDetailView(CurrentCommunityMixin, DetailView):
    ...


class CommunityDetailView(BaseCommunityDetailView):
    ...


community_detail_view = CommunityDetailView.as_view()


class CommunityWelcomeView(LoginRequiredMixin, BaseCommunityDetailView):
    """
    This is shown if the user is not a member (or is not authenticated).

    If user is already a member, redirects to home page.
    """

    template_name = "communities/welcome.html"
    allow_non_members = True

    def get(self, request):
        if rules.test_rule("communities.is_member", request.user, request.community):
            return HttpResponseRedirect(settings.HOME_PAGE_URL)
        return super().get(request)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "join_request": self.get_join_request(),
                "invite": self.get_invite(),
                "is_inactive_member": self.is_inactive_member(),
            }
        )
        return data

    def is_inactive_member(self):
        return rules.test_rule(
            "communities.is_inactive_member",
            self.request.user,
            self.request.community,
        )

    def get_join_request(self):
        return JoinRequest.objects.filter(
            sender=self.request.user,
            community=self.request.community,
            status__in=(
                JoinRequest.Status.PENDING,
                JoinRequest.Status.REJECTED,
            ),
        ).first()

    def get_invite(self):
        return (
            Invite.objects.pending()
            .for_user(self.request.user)
            .filter(community=self.request.community)
            .first()
        )


community_welcome_view = CommunityWelcomeView.as_view()


class CommunityTermsView(BaseCommunityDetailView):
    template_name = "communities/terms.html"


community_terms_view = CommunityTermsView.as_view()


class CommunityNotFoundView(TemplateView):
    """
    This is shown if no community exists for this domain.
    """

    template_name = "communities/not_found.html"

    def get(self, request):
        if request.community.active:
            return HttpResponseRedirect(settings.HOME_PAGE_URL)
        return super().get(request)


community_not_found_view = CommunityNotFoundView.as_view()


class MembershipListView(
    CommunityAdminRequiredMixin,
    MembershipQuerySetMixin,
    SearchMixin,
    ListView,
):
    paginate_by = settings.LONG_PAGE_SIZE
    model = Membership

    def get_queryset(self):
        qs = super().get_queryset().order_by("member__name", "member__username")

        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


membership_list_view = MembershipListView.as_view()


class MembershipDetailView(
    PermissionRequiredMixin,
    MembershipQuerySetMixin,
    DetailView,
):

    permission_required = "communities.view_membership"
    model = Membership


membership_detail_view = MembershipDetailView.as_view()


class MembershipUpdateView(
    SuccessMessageMixin,
    PermissionRequiredMixin,
    MembershipQuerySetMixin,
    TurboUpdateView,
):
    model = Membership
    form_class = MembershipForm
    permission_required = "communities.change_membership"
    success_message = _("Membership has been updated")


membership_update_view = MembershipUpdateView.as_view()


class BaseMembershipDeleteView(
    PermissionRequiredMixin,
    MembershipQuerySetMixin,
    DeleteView,
):
    permission_required = "communities.delete_membership"
    model = Membership


class MembershipDeleteView(BaseMembershipDeleteView):
    def get_success_url(self):
        if self.object.member == self.request.user:
            return settings.HOME_PAGE_URL
        return reverse("communities:membership_list")

    def get_success_message(self):
        return _("You have deleted the membership for %(user)s") % {
            "user": self.object.member.username
        }

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        send_membership_deleted_email(self.object.member, self.object.community)

        messages.success(request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


membership_delete_view = MembershipDeleteView.as_view()


class MembershipLeaveView(BaseMembershipDeleteView):
    """
    Allows the current user to be able to voluntarily leave a community.
    """

    template_name = "communities/membership_leave.html"

    def get_object(self):
        return super().get_queryset().filter(member__pk=self.request.user.id).get()

    def get_success_message(self):
        return _(
            "You have left the community %(community)s"
            % {"community": self.object.community.name}
        )

    def get_success_url(self):
        return settings.HOME_PAGE_URL

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


membership_leave_view = MembershipLeaveView.as_view()
