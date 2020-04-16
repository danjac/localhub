# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse_lazy

from localhub.views import SuccessActionView, SuccessGenericModelView

from ..signals import notification_read
from .mixins import NotificationSuccessRedirectMixin, UnreadNotificationQuerySetMixin


class NotificationMarkAllReadView(
    UnreadNotificationQuerySetMixin,
    NotificationSuccessRedirectMixin,
    SuccessGenericModelView,
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
    success_url = reverse_lazy("notifications:list")

    def post(self, request, *args, **kwargs):
        self.object.is_read = True
        self.object.save()

        notification_read.send(
            sender=self.object.content_object.__class__,
            instance=self.object.content_object,
        )
        return self.success_response()


notification_mark_read_view = NotificationMarkReadView.as_view()
