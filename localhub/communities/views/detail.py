# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.http import HttpResponseRedirect
from django.views.generic import DetailView, TemplateView

from rules.contrib.views import PermissionRequiredMixin

from localhub.invites.models import Invite
from localhub.join_requests.models import JoinRequest

from ..models import Membership
from ..rules import is_inactive_member, is_member
from .mixins import CurrentCommunityMixin, MembershipQuerySetMixin


class BaseCommunityDetailView(CurrentCommunityMixin, DetailView):
    ...


class CommunityDetailView(BaseCommunityDetailView):
    ...


community_detail_view = CommunityDetailView.as_view()


class CommunityWelcomeView(BaseCommunityDetailView):
    """
    This is shown if the user is not a member (or is not authenticated).

    If user is already a member, redirects to home page.
    """

    template_name = "communities/welcome.html"
    allow_non_members = True

    def get(self, request):
        if is_member(request.user, request.community):
            return HttpResponseRedirect(settings.LOCALHUB_HOME_PAGE_URL)
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
        return is_inactive_member(self.request.user, self.request.community)

    def get_join_request(self):
        return JoinRequest.objects.filter(
            sender=self.request.user,
            community=self.request.community,
            status__in=(JoinRequest.Status.PENDING, JoinRequest.Status.REJECTED),
        ).first()

    def get_invite(self):
        return (
            Invite.objects.pending()
            .for_user(self.request.user)
            .filter(community=self.request.community)
            .first()
        )


community_welcome_view = CommunityWelcomeView.as_view()


class CommunitySidebarView(BaseCommunityDetailView):
    """
    Renders sidebar for non-JS browsers.
    """

    template_name = "communities/sidebar.html"


community_sidebar_view = CommunitySidebarView.as_view()


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
            return HttpResponseRedirect(settings.LOCALHUB_HOME_PAGE_URL)
        return super().get(request)


community_not_found_view = CommunityNotFoundView.as_view()


class MembershipDetailView(
    PermissionRequiredMixin, MembershipQuerySetMixin, DetailView,
):

    permission_required = "communities.view_membership"
    model = Membership


membership_detail_view = MembershipDetailView.as_view()
