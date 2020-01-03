# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.http import Http404, HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


class CommunityRequiredMixin:
    """
    Ensures that a community is available on this domain. This requires
    the CurrentCommunityMiddleware is enabled.

    If the user is not a member they will be redirected to the Welcome view.

    If the view has the `allow_non_members` property *True* then the above
    rule is overriden - for example in some cases where we want to allow
    the user to be able to handle an invitation.
    """

    allow_non_members = False

    def dispatch(self, request, *args, **kwargs):
        if not request.community.active:
            return self.handle_community_not_found()

        if (
            not request.user.has_perm("communities.view_community", request.community)
            and not self.allow_non_members
        ):
            return self.handle_community_access_denied()
        return super().dispatch(request, *args, **kwargs)

    def handle_community_access_denied(self):
        if self.request.is_ajax():
            raise PermissionDenied(_("You must be a member of this community"))
        return HttpResponseRedirect(reverse("community_welcome"))

    def handle_community_not_found(self):
        if self.request.is_ajax():
            raise Http404(_("No community is available for this domain"))
        return HttpResponseRedirect(reverse("community_not_found"))


class CommunityLoginRequiredMixin(LoginRequiredMixin, CommunityRequiredMixin):
    """
    Redirects to login instead of welcome page if user not authenticated.
    """

    ...
