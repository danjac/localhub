# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import QuerySet
from django.views.generic import ListView, View, DeleteView
from django.views.generic.detail import SingleObjectMixin
from django.views.generic.list import MultipleObjectMixin
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse

from localite.communities.views import CommunityRequiredMixin
from localite.notifications.models import Notification
from localite.core.types import ContextDict


class NotificationQuerySetMixin(CommunityRequiredMixin, LoginRequiredMixin):
    def get_queryset(self) -> QuerySet:
        return Notification.objects.filter(
            recipient=self.request.user, community=self.request.community
        )


class UnreadNotificationQuerySetMixin(NotificationQuerySetMixin):
    def get_queryset(self) -> QuerySet:
        return super().get_queryset().filter(is_read=False)


class NotificationSuccessMixin:
    def get_success_url(self) -> str:
        return reverse("notifications:list")


class NotificationListView(NotificationQuerySetMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE
    template_name = "notifications/notification_list.html"

    def get_queryset(self) -> QuerySet:
        return (
            super()
            .get_queryset()
            .prefetch_related("content_object")
            .select_related("actor", "content_type")
            .order_by("-created")
        )

    def get_context_data(self, **kwargs) -> ContextDict:
        data = super().get_context_data(**kwargs)
        data["is_unread_notifications"] = (
            self.get_queryset().filter(is_read=False).exists()
        )
        return data


notification_list_view = NotificationListView.as_view()


class NotificationMarkAllReadView(
    UnreadNotificationQuerySetMixin,
    NotificationSuccessMixin,
    MultipleObjectMixin,
    View,
):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.get_queryset().update(is_read=True)
        return HttpResponseRedirect(self.get_success_url())


notification_mark_all_read_view = NotificationMarkAllReadView.as_view()


class NotificationMarkReadView(
    UnreadNotificationQuerySetMixin,
    NotificationSuccessMixin,
    SingleObjectMixin,
    View,
):
    def post(self, request: HttpRequest, *args, **kwargs) -> HttpResponse:
        self.object = self.get_object()
        self.object.is_read = True
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


notification_mark_read_view = NotificationMarkReadView.as_view()


class NotificationDeleteAllView(
    NotificationQuerySetMixin,
    NotificationSuccessMixin,
    MultipleObjectMixin,
    View,
):
    def delete(self, request: HttpRequest) -> str:
        self.get_queryset().delete()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request: HttpRequest) -> HttpResponse:
        return self.delete(request)


notification_delete_all_view = NotificationDeleteAllView.as_view()


class NotificationDeleteView(
    NotificationQuerySetMixin, NotificationSuccessMixin, DeleteView
):
    def get_success_url(self) -> str:
        return reverse("notifications:list")


notification_delete_view = NotificationDeleteView.as_view()
