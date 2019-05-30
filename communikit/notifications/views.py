# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import ListView, View
from django.views.generic.detail import SingleObjectMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from communikit.communities.views import CommunityRequiredMixin
from communikit.core import app_settings
from communikit.notifications.models import Notification


class NotificationListView(
    CommunityRequiredMixin, LoginRequiredMixin, ListView
):
    paginate_by = app_settings.DEFAULT_PAGE_SIZE
    template_name = "notifications/notification_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            Notification.objects.filter(
                recipient=self.request.user, community=self.request.community
            )
            .prefetch_related("content_object")
            .select_related("actor", "content_type")
            .order_by("-created")
        )


notification_list_view = NotificationListView.as_view()


class NotificationMarkReadView(LoginRequiredMixin, SingleObjectMixin, View):
    def get_queryset(self) -> QuerySet:
        return Notification.objects.filter(
            recipient=self.request.user, is_read=False
        )

    def get_success_url(self) -> str:
        return reverse("notifications:list")

    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.is_read = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


notification_mark_read_view = NotificationMarkReadView.as_view()
