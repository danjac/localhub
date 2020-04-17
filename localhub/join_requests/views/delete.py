# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin

from localhub.views import SuccessDeleteView

from ..models import JoinRequest


class JoinRequestDeleteView(PermissionRequiredMixin, SuccessDeleteView):
    model = JoinRequest
    permission_required = "join_requests.delete"

    def get_queryset(self):
        return super().get_queryset().select_related("community", "sender")

    @cached_property
    def is_sender(self):
        return self.object.sender == self.request.user

    def get_success_url(self):
        if self.is_sender:
            if JoinRequest.objects.for_sender(self.request.user).exists():
                return reverse("join_requests:sent_list")
            return settings.LOCALHUB_HOME_PAGE_URL
        return reverse("join_requests:list")

    def get_success_message(self):
        if self.is_sender:
            return _("Your join request for %(community)s has been deleted") % {
                "community": self.object.community.name
            }
        return _("Join request for %(sender)s has been deleted") % {
            "sender": self.object.sender.get_display_name()
        }


join_request_delete_view = JoinRequestDeleteView.as_view()
