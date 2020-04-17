# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin

from localhub.communities.views import CommunityRequiredMixin
from localhub.views import SuccessCreateView

from ..emails import send_join_request_email
from ..forms import JoinRequestForm
from ..models import JoinRequest


class JoinRequestCreateView(
    PermissionRequiredMixin, CommunityRequiredMixin, SuccessCreateView,
):
    model = JoinRequest
    form_class = JoinRequestForm
    template_name = "join_requests/joinrequest_form.html"
    allow_non_members = True
    permission_required = "join_requests.create"
    success_message = _("Your request has been sent to the community admins")

    def get_permission_object(self):
        return self.request.community

    def get_form(self, *args, **kwargs):
        return self.get_form_class()(
            self.request.user, self.request.community, *args, **kwargs
        )

    def get_success_url(self):
        return reverse("community_welcome")

    def form_valid(self, form):
        self.object = form.save()
        send_join_request_email(self.object)
        return self.success_response()


join_request_create_view = JoinRequestCreateView.as_view()
