# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse_lazy

from localhub.communities.views import CommunityRequiredMixin

from ..models import Notification


class NotificationQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Notification.objects.for_community(self.request.community).for_recipient(
            self.request.user
        )


class UnreadNotificationQuerySetMixin(NotificationQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().unread()


class NotificationSuccessRedirectMixin:
    success_url = reverse_lazy("notifications:list")
