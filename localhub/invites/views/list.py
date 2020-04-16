# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.utils.functional import cached_property
from vanilla import ListView

from localhub.views import SearchMixin

from ..models import Invite
from .mixins import InviteAdminMixin, InviteQuerySetMixin, InviteRecipientQuerySetMixin


class InviteListView(InviteAdminMixin, InviteQuerySetMixin, SearchMixin, ListView):
    """
    TBD: list of received pending community invitations
    + counter template tag
    """

    model = Invite
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE

    def get_permission_object(self):
        return self.request.community

    def get_queryset(self):
        qs = super().get_queryset()
        if self.search_query:
            qs = qs.filter(email__icontains=self.search_query)

        if self.status:
            qs = qs.filter(status=self.status)

        return qs.order_by("-created")

    @cached_property
    def status(self):
        status = self.request.GET.get("status")
        if status in Invite.Status.values and self.total_count:
            return status
        return None

    @cached_property
    def status_display(self):
        return dict(Invite.Status.choices)[self.status] if self.status else None

    @cached_property
    def total_count(self):
        return super().get_queryset().count()

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "total_count": self.total_count,
                "status": self.status,
                "status_display": self.status_display,
                "status_choices": list(Invite.Status.choices),
            }
        )
        return data


invite_list_view = InviteListView.as_view()


class ReceivedInviteListView(InviteRecipientQuerySetMixin, ListView):
    """
    List of pending invites sent to this user from different communities.
    """

    template_name = "invites/received_invite_list.html"
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE

    def get_queryset(self):
        return super().get_queryset().order_by("-created")


received_invite_list_view = ReceivedInviteListView.as_view()
