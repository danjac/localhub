# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings
from django.views.generic import DeleteView
from rules.contrib.views import PermissionRequiredMixin

from .mixins import CurrentUserMixin


class UserDeleteView(CurrentUserMixin, PermissionRequiredMixin, DeleteView):
    permission_required = "users.delete_user"
    success_url = settings.LOCALHUB_HOME_PAGE_URL
    template_name = "users/user_confirm_delete.html"


user_delete_view = UserDeleteView.as_view()
