# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import no_type_check

from django.contrib.auth.views import redirect_to_login
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView, ListView, TemplateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from communikit.communities.forms import MembershipForm
from communikit.communities.models import Community, Membership


class CommunityRequiredMixin:
    """
    Ensures that a community is available on this domain. This requires
    the CurrentCommunityMiddleware is enabled.
    """

    allow_if_private = False
    request: HttpRequest

    @no_type_check
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.community:
            return self.handle_community_not_found()

        if (
            not request.user.has_perm(
                "communities.view_community", request.community
            )
            and not self.allow_if_private
        ):
            return self.handle_community_access_denied()
        return super().dispatch(request, *args, **kwargs)

    def handle_community_access_denied(self) -> HttpResponse:
        if self.request.is_ajax():
            raise PermissionDenied(_("You must be a member of this community"))
        if self.request.user.is_anonymous:
            return redirect_to_login(self.request.get_full_path())
        return HttpResponseRedirect(reverse("community_access_denied"))

    def handle_community_not_found(self) -> HttpResponse:
        if self.request.is_ajax():
            raise Http404(_("No community is available for this domain"))
        return HttpResponseRedirect(reverse("community_not_found"))


class CommunityNotFoundView(TemplateView):
    """
    This is shown if no community exists for this domain.
    """

    template_name = "communities/not_found.html"


community_not_found_view = CommunityNotFoundView.as_view()


class CommunityAccessDeniedView(TemplateView):
    """
    This is shown if no community exists for this domain.
    """

    template_name = "communities/access_denied.html"


community_access_denied_view = CommunityAccessDeniedView.as_view()


class CommunityUpdateView(
    CommunityRequiredMixin,
    PermissionRequiredMixin,
    SuccessMessageMixin,
    UpdateView,
):
    fields = ("name", "description", "public")

    permission_required = "communities.manage_community"
    success_message = _("Community settings have been updated")

    def get_object(self) -> Community:
        return self.request.community

    def get_success_url(self) -> str:
        return self.request.path


community_update_view = CommunityUpdateView.as_view()


class MembershipQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Membership.objects.filter(
            community=self.request.community
        ).select_related("community", "member")


class SingleMembershipMixin(MembershipQuerySetMixin, SingleObjectMixin):
    ...


class MultipleMembershipMixin(MembershipQuerySetMixin, MultipleObjectMixin):
    ...


class MembershipListView(
    PermissionRequiredMixin, MultipleMembershipMixin, ListView
):
    paginate_by = 30
    allow_empty = True
    permission_required = "communities.manage_community"

    def get_permission_object(self) -> Community:
        return self.request.community

    def get_queryset(self) -> QuerySet:
        return super().get_queryset().order_by("member__username")


membership_list_view = MembershipListView.as_view()


class MembershipUpdateView(
    PermissionRequiredMixin,
    SingleMembershipMixin,
    SuccessMessageMixin,
    UpdateView,
):
    form_class = MembershipForm
    permission_required = "communities.change_membership"
    success_url = reverse_lazy("communities:membership_list")
    success_message = _("Membership has been updated")


membership_update_view = MembershipUpdateView.as_view()


class MembershipDeleteView(
    PermissionRequiredMixin, SingleMembershipMixin, DeleteView
):
    fields = ("role", "active")
    permission_required = "communities.delete_membership"
    success_url = reverse_lazy("communities:membership_list")


membership_delete_view = MembershipDeleteView.as_view()
