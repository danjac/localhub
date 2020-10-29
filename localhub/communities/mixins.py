# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext as _

# Third Party Libraries
from rules.contrib.views import PermissionRequiredMixin

# Local
from .models import Community, Membership


class CommunityRequiredMixin:
    """
    Ensures that a community is available on this domain. This requires
    the CurrentCommunityMiddleware is enabled.

    If the community is not public, the user will be redirected to the Welcome view
    if they are not a member, unless the `allow_non_members` attribute is True.
    """

    allow_non_members = False

    def dispatch(self, request, *args, **kwargs):
        if not request.community.active:
            return self.handle_community_not_found()

        if (
            not request.user.has_perm("communities.view_community", request.community)
            and not self.is_non_members_allowed()
        ):
            return self.handle_community_access_denied()
        return super().dispatch(request, *args, **kwargs)

    def is_non_members_allowed(self):
        if self.allow_non_members:
            return True
        return self.request.community.public

    def handle_community_access_denied(self):
        if self.request.is_ajax():
            raise PermissionDenied(_("You must be a member of this community"))
        return HttpResponseRedirect(reverse("community_welcome"))

    def handle_community_not_found(self):
        if self.request.is_ajax():
            raise Http404(_("No community is available for this domain"))
        return HttpResponseRedirect(reverse("community_not_found"))


class CurrentCommunityMixin(CommunityRequiredMixin):
    model = Community

    def get_object(self):
        return self.request.community


class CommunityPermissionRequiredMixin(CommunityRequiredMixin, PermissionRequiredMixin):
    def get_permission_object(self):
        return self.request.community


class CommunityModeratorRequiredMixin(CommunityPermissionRequiredMixin):
    permission_required = "communities.moderate_community"


class CommunityAdminRequiredMixin(CommunityPermissionRequiredMixin):
    permission_required = "communities.manage_community"


class MembershipQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Membership.objects.filter(
            community=self.request.community
        ).select_related("community", "member")
