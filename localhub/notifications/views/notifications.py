# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from vanilla import ListView

from localhub.communities.views import CommunityRequiredMixin
from localhub.views import SuccessActionView, SuccessDeleteView, SuccessGenericModelView

from ..models import Notification
from ..signals import notification_read


class NotificationQuerySetMixin(CommunityRequiredMixin):
    def get_queryset(self):
        return Notification.objects.for_community(self.request.community).for_recipient(
            self.request.user
        )


class UnreadNotificationQuerySetMixin(NotificationQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().unread()


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


class NotificationSuccessRedirectMixin:
    success_url = reverse_lazy("notifications:list")


class NotificationMarkAllReadView(
    UnreadNotificationQuerySetMixin,
    NotificationSuccessRedirectMixin,
    SuccessGenericModelView,
):
    success_url = reverse_lazy("notifications:list")

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


class NotificationDeleteAllView(
    NotificationQuerySetMixin, NotificationSuccessRedirectMixin, SuccessGenericModelView
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
