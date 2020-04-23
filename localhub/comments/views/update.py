# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rules.contrib.views import PermissionRequiredMixin

from localhub.views import SuccessUpdateView

from ..forms import CommentForm
from ..models import Comment
from .mixins import CommentQuerySetMixin


class CommentUpdateView(
    PermissionRequiredMixin, CommentQuerySetMixin, SuccessUpdateView,
):
    form_class = CommentForm
    model = Comment
    permission_required = "comments.change_comment"
    success_message = _("Your %(model)s has been updated")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["content_object"] = self.object.get_content_object()
        return context

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.editor = self.request.user
        self.object.edited = timezone.now()
        self.object.save()

        self.object.notify_on_update()
        return self.success_response()


comment_update_view = CommentUpdateView.as_view()
