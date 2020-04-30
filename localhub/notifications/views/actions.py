# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponseRedirect

from localhub.common.views import SuccessActionView, SuccessDeleteView, SuccessView

from ..signals import notification_read
from .mixins import (
    NotificationQuerySetMixin,
    NotificationSuccessRedirectMixin,
    UnreadNotificationQuerySetMixin,
)


class NotificationMarkAllReadView(
    UnreadNotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessView,
):
    def post(self, request, *args, **kwargs):
        qs = self.get_queryset()
        [
            notification_read.send(
                sender=notification.content_object.__class__,
                instance=notification.content_object,
            )
            for notification in qs.prefetch_related("content_object")
        ]
        qs.update(is_read=True)
        return self.success_response()


notification_mark_all_read_view = NotificationMarkAllReadView.as_view()


class NotificationMarkReadView(
    UnreadNotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessActionView
):
    def post(self, request, *args, **kwargs):
        self.object.is_read = True
        self.object.save()

        notification_read.send(
            sender=self.object.content_object.__class__,
            instance=self.object.content_object,
        )
        return self.success_response()


notification_mark_read_view = NotificationMarkReadView.as_view()


class NotificationDeleteAllView(
    NotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessView
):
    def delete(self, request):
        self.get_queryset().delete()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request):
        return self.delete(request)


notification_delete_all_view = NotificationDeleteAllView.as_view()


class NotificationDeleteView(
    NotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessDeleteView
):

    ...


notification_delete_view = NotificationDeleteView.as_view()
