# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import http
import json

# Django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse
from django.views.decorators.http import require_POST

# Third Party Libraries
from turbo_response import TurboStream

# Localhub
from localhub.common.pagination import render_paginated_queryset
from localhub.communities.decorators import community_required

# Local
from .models import Notification, PushSubscription
from .signals import notification_read


@login_required
@community_required
def notification_list_view(request):
    qs = (
        get_notification_queryset(request)
        .exclude_blocked_actors(request.user)
        .prefetch_related("content_object")
        .select_related("actor", "content_type", "community", "recipient")
        .order_by("is_read", "-created")
    )

    return render_paginated_queryset(
        request,
        qs,
        "notifications/notification_list.html",
        {
            "is_unread_notifications": qs.filter(is_read=False).exists(),
            "webpush_settings": {
                "public_key": settings.VAPID_PUBLIC_KEY,
                "enabled": settings.WEBPUSH_ENABLED,
            },
        },
        page_size=settings.LONG_PAGE_SIZE,
    )


@require_POST
@login_required
@community_required
def notification_mark_all_read_view(request):
    qs = get_unread_notification_queryset(request)
    [
        notification_read.send(
            sender=notification.content_object.__class__,
            instance=notification.content_object,
        )
        for notification in qs.prefetch_related("content_object")
    ]
    qs.update(is_read=True)
    return redirect("notifications:list")


@require_POST
@login_required
@community_required
def notification_mark_read_view(request, pk):
    obj = get_object_or_404(get_unread_notification_queryset(request), pk=pk)
    obj.is_read = True
    obj.save()
    notification_read.send(
        sender=obj.content_object.__class__,
        instance=obj.content_object,
    )

    target = (
        f"notification-{obj.id}"
        if Notification.objects.filter(recipient=request.user, is_read=False).exists()
        else "notifications"
    )
    return TurboStream(target).remove.response()


@require_POST
@login_required
@community_required
def notification_delete_all_view(request):
    get_notification_queryset(request).delete()
    return redirect("notifications:list")


@require_POST
@login_required
@community_required
def notification_delete_view(request, pk):
    obj = get_object_or_404(get_notification_queryset(request), pk=pk)
    target = f"notification-{obj.id}"
    obj.delete()
    return TurboStream(target).remove.response()


@require_POST
@login_required
@community_required
def subscribe_view(request, remove=False):

    try:
        json_body = json.loads(request.body.decode("utf-8"))

        data = {"endpoint": json_body["endpoint"]}
        keys = json_body["keys"]
        data["auth"] = keys["auth"]
        data["p256dh"] = keys["p256dh"]

    except (ValueError, KeyError):
        return HttpResponseBadRequest()

    data |= {"user": request.user, "community": request.community}

    if remove:
        PushSubscription.objects.filter(**data).delete()
        status = http.HTTPStatus.OK
    else:
        try:
            _, created = PushSubscription.objects.get_or_create(**data)
            status = http.HTTPStatus.CREATED if created else http.HTTPStatus.OK
        except IntegrityError:
            pass  # dupe, ignore
    return JsonResponse({"message": "ok"}, status=status)


def service_worker_view(request):
    """
    Returns template containing serviceWorker JS, can't use
    static as must always be under domain. We can also pass
    in server specific settings.
    """

    return TemplateResponse(
        request,
        "notifications/service_worker.js",
        {"vapid_public_key": settings.VAPID_PUBLIC_KEY},
        content_type="application/javascript",
    )


def get_notification_queryset(request):
    return Notification.objects.for_community(request.community).filter(
        recipient=request.user
    )


def get_unread_notification_queryset(request):
    return get_notification_queryset(request).filter(is_read=False)
