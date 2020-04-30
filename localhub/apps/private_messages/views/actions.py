# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import IntegrityError
from django.urls import reverse, reverse_lazy
from django.utils.translation import gettext_lazy as _

from localhub.apps.bookmarks.models import Bookmark
from localhub.common.views import SuccessActionView, SuccessDeleteView, SuccessView

from ..models import Message
from .mixins import RecipientQuerySetMixin, SenderOrRecipientQuerySetMixin


class MessageMarkAllReadView(RecipientQuerySetMixin, SuccessView):
    success_url = reverse_lazy("private_messages:inbox")

    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.get_queryset().for_recipient(self.request.user).mark_read()
        return self.success_response()


message_mark_all_read_view = MessageMarkAllReadView.as_view()


class MessageMarkReadView(RecipientQuerySetMixin, SuccessActionView):
    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.object.mark_read()
        return self.success_response()


message_mark_read_view = MessageMarkReadView.as_view()


class BaseMessageBookmarkView(SenderOrRecipientQuerySetMixin, SuccessActionView):
    is_success_ajax_response = True


class MessageBookmarkView(BaseMessageBookmarkView):
    success_message = _("You have bookmarked this message")

    def post(self, request, *args, **kwargs):
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            pass
        return self.success_response()


message_bookmark_view = MessageBookmarkView.as_view()


class MessageRemoveBookmarkView(BaseMessageBookmarkView):
    success_message = _("You have removed this message from your bookmarks")

    def post(self, request, *args, **kwargs):
        Bookmark.objects.filter(user=request.user, message=self.object).delete()
        return self.success_response()

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


message_remove_bookmark_view = MessageRemoveBookmarkView.as_view()


class MessageDeleteView(SenderOrRecipientQuerySetMixin, SuccessDeleteView):
    """
    Does a "soft delete" which sets sender/recipient deleted flag
    accordingly.

    If both sender and recipient have soft-deleted, then the message
    is "hard" deleted.
    """

    model = Message
    success_message = _("You have deleted this message")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete(self.request.user)
        return self.success_response()

    def get_success_url(self):
        if self.request.user == self.object.recipient:
            return reverse("private_messages:inbox")
        return reverse("private_messages:outbox")


message_delete_view = MessageDeleteView.as_view()
