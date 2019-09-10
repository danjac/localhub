# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.views.generic import View

from vanilla import DeleteView, ListView, TemplateView, GenericModelView

from localhub.communities.views import CommunityRequiredMixin
from localhub.notifications.models import Notification, PushSubscription


class NotificationQuerySetMixin(LoginRequiredMixin, CommunityRequiredMixin):
    def get_queryset(self):
        return Notification.objects.for_community(
            self.request.community
        ).filter(recipient=self.request.user)


class UnreadNotificationQuerySetMixin(NotificationQuerySetMixin):
    def get_queryset(self):
        return super().get_queryset().filter(is_read=False)


class NotificationSuccessRedirectMixin:
    def get_success_url(self):
        return reverse("notifications:list")


class BasePushSubscriptionView(
    CommunityRequiredMixin, LoginRequiredMixin, View
):
    def post(self, request, *args, **kwargs):
        try:
            json_body = json.loads(request.body.decode("utf-8"))

            data = {"endpoint": json_body["endpoint"]}
            keys = json_body["keys"]
            data["auth"] = keys["auth"]
            data["p256dh"] = keys["p256dh"]

        except (ValueError, KeyError):
            return HttpResponse(status=400)

        return self.handle_action(request, **data)

    def handle_action(self, request, auth, p256dh, endpoint):
        raise NotImplementedError


class NotificationListView(NotificationQuerySetMixin, ListView):
    paginate_by = settings.DEFAULT_PAGE_SIZE
    template_name = "notifications/notification_list.html"
    model = Notification

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .prefetch_related("content_object")
            .select_related("actor", "content_type")
            .exclude(actor__in=self.request.user.blocked.all())
            .order_by("is_read", "-created")
        )

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["is_unread_notifications"] = (
            self.get_queryset().filter(is_read=False).exists()
        )
        return data


notification_list_view = NotificationListView.as_view()


class NotificationMarkAllReadView(
    UnreadNotificationQuerySetMixin,
    NotificationSuccessRedirectMixin,
    GenericModelView,
):
    def post(self, request, *args, **kwargs):
        self.get_queryset().update(is_read=True)
        return HttpResponseRedirect(self.get_success_url())


notification_mark_all_read_view = NotificationMarkAllReadView.as_view()


class NotificationMarkReadView(
    UnreadNotificationQuerySetMixin,
    NotificationSuccessRedirectMixin,
    GenericModelView,
):
    def post(self, request, *args, **kwargs):
        notification = self.get_object()
        notification.is_read = True
        notification.save()
        return HttpResponseRedirect(self.get_success_url())


notification_mark_read_view = NotificationMarkReadView.as_view()


class NotificationDeleteAllView(
    NotificationQuerySetMixin,
    NotificationSuccessRedirectMixin,
    GenericModelView,
):
    def delete(self, request):
        self.get_queryset().delete()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request):
        return self.delete(request)


notification_delete_all_view = NotificationDeleteAllView.as_view()


class NotificationDeleteView(
    NotificationQuerySetMixin, NotificationSuccessRedirectMixin, DeleteView
):
    ...


notification_delete_view = NotificationDeleteView.as_view()


class ServiceWorkerView(TemplateView):
    """
    Returns template containing serviceWorker JS, can't use
    static as must always be under domain. We can also pass
    in server specific settings.
    """

    template_name = "notifications/service_worker.js"
    content_type = "application/javascript"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["vapid_public_key"] = settings.VAPID_PUBLIC_KEY
        return data


service_worker_view = ServiceWorkerView.as_view()


class SubscribeView(BasePushSubscriptionView):
    def handle_action(self, request, auth, p256dh, endpoint):

        try:
            PushSubscription.objects.get_or_create(
                auth=auth,
                p256dh=p256dh,
                endpoint=endpoint,
                user=request.user,
                community=request.community,
            )
        except IntegrityError:
            pass  # dupe, ignore

        return JsonResponse({"message": "ok"}, status=201)


subscribe_view = SubscribeView.as_view()


class UnsubscribeView(BasePushSubscriptionView):
    def handle_action(self, request, auth, p256dh, endpoint):

        PushSubscription.objects.filter(
            auth=auth,
            p256dh=p256dh,
            endpoint=endpoint,
            user=request.user,
            community=request.community,
        ).delete()

        return JsonResponse({"message": "ok"}, status=200)


unsubscribe_view = UnsubscribeView.as_view()
