# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.common.views import SuccessDeleteView

from ..emails import send_membership_deleted_email
from ..models import Membership
from .mixins import MembershipQuerySetMixin


class BaseMembershipDeleteView(
    PermissionRequiredMixin, MembershipQuerySetMixin, SuccessDeleteView,
):
    permission_required = "communities.delete_membership"
    model = Membership


class MembershipDeleteView(BaseMembershipDeleteView):
    def get_success_url(self):
        if self.object.member == self.request.user:
            return settings.LOCALHUB_HOME_PAGE_URL
        return reverse("communities:membership_list")

    def get_success_message(self):
        return _("You have deleted the membership for %(user)s") % {
            "user": self.object.member.username
        }

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()

        send_membership_deleted_email(self.object.member, self.object.community)

        return self.success_response()


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
        return settings.LOCALHUB_HOME_PAGE_URL

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.delete()
        return self.success_response()


membership_leave_view = MembershipLeaveView.as_view()
