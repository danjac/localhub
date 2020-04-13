# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from rules.contrib.views import PermissionRequiredMixin
from vanilla import DeleteView

from localhub.views import SuccessMixin

from .mixins import CommentQuerySetMixin


class CommentDeleteView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessMixin, DeleteView,
):
    permission_required = "comments.delete_comment"
    template_name = "comments/comment_confirm_delete.html"
    success_message = _("This comment has been deleted")

    def get_success_url(self):
        obj = self.object.get_content_object()
        if obj:
            return obj.get_absolute_url()
        return reverse("comments:list")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.request.user != self.object.owner:
            self.object.soft_delete()
            self.object.notify_on_delete(self.request.user)
        else:
            self.object.delete()

        return self.success_response()


comment_delete_view = CommentDeleteView.as_view()
