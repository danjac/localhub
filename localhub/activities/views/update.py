# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.views import SuccessUpdateView

from ..forms import ActivityTagsForm
from .mixins import ActivityQuerySetMixin, ActivityTemplateMixin


class ActivityUpdateView(
    PermissionRequiredMixin,
    ActivityQuerySetMixin,
    ActivityTemplateMixin,
    SuccessUpdateView,
):
    permission_required = "activities.change_activity"
    success_message = _("Your %(model)s has been updated")

    def form_valid(self, form):

        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.edited = timezone.now()
        self.object.save()

        self.object.update_reshares()

        if self.object.published:
            self.object.notify_on_update()

        return self.success_response()


class ActivityUpdateTagsView(ActivityUpdateView):
    """
    Allows a moderator to update the tags on a view, e.g
    to add a "content sensitive" tag.
    """

    form_class = ActivityTagsForm
    permission_required = "activities.change_activity_tags"
    success_message = _("Tags have been updated")

    def get_queryset(self):
        return super().get_queryset().published()
