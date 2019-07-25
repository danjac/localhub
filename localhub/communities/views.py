# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from typing import no_type_check

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.exceptions import PermissionDenied
from django.db.models import QuerySet
from django.forms import ModelForm
from django.http import (
    Http404,
    HttpRequest,
    HttpResponse,
    HttpResponseRedirect,
)
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import (
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.views.generic.detail import SingleObjectMixin

from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.forms import MembershipForm
from localhub.communities.models import Community, Membership


class CommunityRequiredMixin:
    """
    Ensures that a community is available on this domain. This requires
    the CurrentCommunityMiddleware is enabled.

    If the community is private and the user is not a member then they
    are shown an "Access Denied" screen. If they are not yet logged in,
    then they are redirected to the login page first to authenticate so
    their membership can be properly verified.

    If the view has the `allow_if_private` property *True* then the above
    rule is overriden - for example in some cases where we want to allow
    the user to be able to handle an invitation.
    """

    allow_if_private = False
    request: HttpRequest

    @no_type_check
    def dispatch(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not request.community.active:
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


class CommunityDetailView(CommunityRequiredMixin, DetailView):
    def get_object(self) -> Community:
        return self.request.community


community_detail_view = CommunityDetailView.as_view()


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
    CommunityRequiredMixin, PermissionRequiredMixin, UpdateView
):
    fields = (
        "name",
        "description",
        "terms",
        "content_warning_tags",
        "public",
        "email_domain",
    )

    permission_required = "communities.manage_community"
    success_message = _("Community settings have been updated")

    def get_object(self) -> Community:
        return self.request.community

    def get_success_url(self) -> str:
        return self.request.path

    def get_success_message(self) -> str:
        return self.success_message

    def form_valid(self, form: ModelForm) -> HttpResponse:
        community = form.save(commit=False)
        community.admin = self.request.user
        community.save()
        messages.success(self.request, self.get_success_message())
        return HttpResponseRedirect(self.get_success_url())


community_update_view = CommunityUpdateView.as_view()


class CommunityListView(LoginRequiredMixin, ListView):
    """
    Returns all communities a user belongs to
    """

    paginate_by = settings.DEFAULT_PAGE_SIZE
    allow_empty = True

    def get_queryset(self) -> QuerySet:
        return self.request.user.membership_set.select_related(
            "community"
        ).order_by("community__name")


community_list_view = CommunityListView.as_view()


class MembershipQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Membership.objects.filter(
            community=self.request.community
        ).select_related("community", "member")


class SingleMembershipMixin(MembershipQuerySetMixin, SingleObjectMixin):
    ...


class MembershipListView(
    LoginRequiredMixin,
    PermissionRequiredMixin,
    MembershipQuerySetMixin,
    ListView,
):
    paginate_by = settings.DEFAULT_PAGE_SIZE
    permission_required = "communities.manage_community"

    def get_queryset(self) -> QuerySet:
        return (
            super().get_queryset().order_by("member__name", "member__username")
        )

    def get_permission_object(self) -> Community:
        return self.request.community


membership_list_view = MembershipListView.as_view()


class MembershipUpdateView(
    LoginRequiredMixin,
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
    LoginRequiredMixin,
    PermissionRequiredMixin,
    SingleMembershipMixin,
    DeleteView,
):
    permission_required = "communities.delete_membership"

    def get_success_url(self) -> str:
        if self.object.member == self.request.user:
            return reverse("communities:community_list")
        return reverse("communities:membership_list")


membership_delete_view = MembershipDeleteView.as_view()


class CommunityLeaveView(MembershipDeleteView):
    """
    Allows the current user to be able to leave the community.
    """

    template_name = "communities/leave.html"

    def get_object(self) -> Membership:
        return (
            super()
            .get_queryset()
            .filter(member__pk=self.request.user.id)
            .get()
        )

    def get_success_url(self) -> str:
        return settings.HOME_PAGE_URL


community_leave_view = CommunityLeaveView.as_view()
