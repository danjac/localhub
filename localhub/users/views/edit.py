# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils.translation import gettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.views import SuccessUpdateView

from ..forms import UserForm
from .mixins import CurrentUserMixin


class UserUpdateView(
    CurrentUserMixin, PermissionRequiredMixin, SuccessUpdateView,
):
    permission_required = "users.change_user"
    success_message = _("Your details have been updated")
    form_class = UserForm
    template_name = "users/user_form.html"

    def get_success_url(self):
        return self.request.path

    def form_valid(self, form):
        self.object = form.save()
        self.object.notify_on_update()
        return self.success_response()


user_update_view = UserUpdateView.as_view()
