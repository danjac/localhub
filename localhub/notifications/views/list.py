# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from vanilla import ListView

from ..models import Notification
from .mixins import NotificationQuerySetMixin


class NotificationListView(NotificationQuerySetMixin, ListView):
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE
    template_name = "notifications/notification_list.html"
    model = Notification

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .exclude_blocked_actors(self.request.user)
            .prefetch_related("content_object")
            .select_related("actor", "content_type", "community", "recipient")
            .order_by("is_read", "-created")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["is_unread_notifications"] = (
            self.get_queryset().filter(is_read=False).exists()
        )
        return data


notification_list_view = NotificationListView.as_view()
