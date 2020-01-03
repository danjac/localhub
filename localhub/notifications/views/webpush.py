# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import json

from django.conf import settings
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.generic import View
from vanilla import TemplateView

from localhub.communities.views import CommunityLoginRequiredMixin

from ..models import PushSubscription


class BasePushSubscriptionView(CommunityLoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            json_body = json.loads(request.body.decode("utf-8"))

            data = {"endpoint": json_body["endpoint"]}
            keys = json_body["keys"]
            data["auth"] = keys["auth"]
            data["p256dh"] = keys["p256dh"]

        except (ValueError, KeyError):
            return HttpResponseBadRequest()

        return self.handle_action(request, **data)

    def handle_action(self, request, auth, p256dh, endpoint):
        raise NotImplementedError


class ServiceWorkerView(TemplateView):
    """
    Returns template containing serviceWorker JS, can't use
    static as must always be under domain. We can also pass
    in server specific settings.
    """

    template_name = "notifications/service_worker.js"

    def get(self, request):
        response = super().get(request)
        response["Content-Type"] = "application/javascript"
        return response

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
