# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from vanilla import GenericModelView

from localhub.bookmarks.models import Bookmark
from localhub.views import SuccessMixin

from .mixins import RecipientQuerySetMixin, SenderOrRecipientQuerySetMixin


class MessageMarkReadView(RecipientQuerySetMixin, SuccessMixin, GenericModelView):
    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.mark_read()
        return self.success_response()


message_mark_read_view = MessageMarkReadView.as_view()


class MessageMarkAllReadView(RecipientQuerySetMixin, GenericModelView):
    def get_queryset(self):
        return super().get_queryset().unread()

    def post(self, request, *args, **kwargs):
        self.get_queryset().for_recipient(self.request.user).mark_read()
        return HttpResponseRedirect(reverse("private_messages:inbox"))


message_mark_all_read_view = MessageMarkAllReadView.as_view()


class BaseMessageBookmarkView(
    SenderOrRecipientQuerySetMixin, SuccessMixin, GenericModelView
):
    template_name = "private_messages/includes/bookmark.html"

    def success_response(self, has_bookmarked):
        return self.render_success_to_response(
            {"message": self.object, "has_bookmarked": has_bookmarked}
        )


class MessageBookmarkView(BaseMessageBookmarkView):
    success_message = _("You have bookmarked this message")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        try:
            Bookmark.objects.create(
                user=request.user,
                community=request.community,
                content_object=self.object,
            )
        except IntegrityError:
            pass
        return self.success_response(has_bookmarked=True)


message_bookmark_view = MessageBookmarkView.as_view()


class MessageRemoveBookmarkView(BaseMessageBookmarkView):
    success_message = _("You have removed this message from your bookmarks")

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        Bookmark.objects.filter(user=request.user, message=self.object).delete()
        return self.success_response(has_bookmarked=False)

    def delete(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)


message_remove_bookmark_view = MessageRemoveBookmarkView.as_view()
