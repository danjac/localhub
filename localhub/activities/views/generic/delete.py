# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import DeleteView

from localhub.views import SuccessMixin


from .mixins import ActivityQuerySetMixin, ActivityTemplateMixin


class ActivityDeleteView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    SuccessMixin,
    DeleteView,
):
    permission_required = "activities.delete_activity"
    success_message = _("This %(model)s has been deleted")

    def get_success_url(self):
        if self.object.deleted or self.object.published:
            return settings.LOCALHUB_HOME_PAGE_URL
        return reverse("activities:private")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        return self.success_response()
