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
from localhub.invites.models import Invite
from localhub.join_requests.models import JoinRequest

# Local
from .emails import send_membership_deleted_email
from .forms import CommunityForm, MembershipForm
from .mixins import (
    CommunityAdminRequiredMixin,
    CurrentCommunityMixin,
    MembershipQuerySetMixin,
)
from .models import Community, Membership


class CommunityListView(SearchMixin, ListView):
    """
    Returns all public communities, or communities the
    current user belongs to.

    TBD: list invites (matching email)
    """

    paginate_by = settings.DEFAULT_PAGE_SIZE
    template_name = "communities/community_list.html"

    def get_queryset(self):
        qs = Community.objects.accessible(self.request.user).order_by("name")
        if self.search_query:
            qs = qs.filter(name__icontains=self.search_query)
        return qs

    def get_member_communities(self):
        if self.request.user.is_anonymous:
            return Community.objects.none()
        return Community.objects.filter(
            membership__member=self.request.user, membership__active=True
        ).exclude(pk=self.request.community.id)

    def get_available_users(self):
        user_model = get_user_model()

        if self.request.user.is_anonymous:
            return user_model.none()
        return user_model.objects.filter(is_active=True).exclude(
            pk__in=self.request.user.blocked.all()
        )

    def get_notifications_count(self):
        if self.request.user.is_anonymous:
            return {}

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
        if self.request.user.is_anonymous:
            return {}

        return dict(
            self.get_member_communities()
            .filter(
                membership__role__in=(
                    Membership.Role.ADMIN,
                    Membership.Role.MODERATOR,
                )
            )
            .annotate(num_flags=Count("flag", distinct=True))
            .values_list("id", "num_flags")
        )

    def get_messages_count(self):
        if self.request.user.is_anonymous:
            return {}

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
        if self.request.user.is_anonymous:
            return {}

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
