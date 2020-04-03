# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import DeleteView, DetailView, ListView, UpdateView

from localhub.views import SearchMixin

from ..emails import send_membership_deleted_email
from ..forms import MembershipForm
from ..models import Membership
from .base import CommunityRequiredMixin


class MembershipQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Membership.objects.filter(
            community=self.request.community
        ).select_related("community", "member")


class MembershipListView(
    PermissionRequiredMixin, MembershipQuerySetMixin, SearchMixin, ListView,
):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE
    permission_required = "communities.manage_community"
    model = Membership

    def get_permission_object(self):
        return self.request.community

    def get_queryset(self):

        qs = super().get_queryset().order_by("member__name", "member__username")

        if self.search_query:
            qs = qs.search(self.search_query)
        return qs


membership_list_view = MembershipListView.as_view()


class MembershipDetailView(
    PermissionRequiredMixin, MembershipQuerySetMixin, DetailView,
):

    permission_required = "communities.view_membership"
    model = Membership


membership_detail_view = MembershipDetailView.as_view()


class MembershipUpdateView(
    PermissionRequiredMixin, MembershipQuerySetMixin, SuccessMessageMixin, UpdateView,
):
    model = Membership
    form_class = MembershipForm
    permission_required = "communities.change_membership"
    success_message = _("Membership has been updated")

    def get_success_url(self):
        return reverse("communities:membership_detail", args=[self.object.id])


membership_update_view = MembershipUpdateView.as_view()


class MembershipDeleteView(
    PermissionRequiredMixin, MembershipQuerySetMixin, DeleteView,
):
    permission_required = "communities.delete_membership"
    model = Membership

    def get_success_url(self):
        if self.object.member == self.request.user:
            return settings.LOCALHUB_HOME_PAGE_URL
        return reverse("communities:membership_list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        messages.success(
            self.request,
            _("Membership for user %s has been deleted") % self.object.member.username,
        )
        send_membership_deleted_email(self.object.member, self.object.community)
        return HttpResponseRedirect(self.get_success_url())


membership_delete_view = MembershipDeleteView.as_view()


class MembershipLeaveView(MembershipDeleteView):
    """
    Allows the current user to be able to voluntarily leave a community.
    """

    template_name = "communities/membership_leave.html"

    def get_object(self):
        return super().get_queryset().filter(member__pk=self.request.user.id).get()

    def get_success_url(self):
        return settings.LOCALHUB_HOME_PAGE_URL


membership_leave_view = MembershipLeaveView.as_view()
