# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views import (
    notification_delete_all_view,
    notification_delete_view,
    notification_list_view,
    notification_mark_all_read_view,
    notification_mark_read_view,
    service_worker_view,
    subscribe_view,
    unsubscribe_view,
)

app_name = "notifications"

urlpatterns = [
    path("", notification_list_view, name="list"),
    path("service-worker.js", service_worker_view, name="service_worker"),
    path("~subscribe/", subscribe_view, name="subscribe"),
    path("~unsubscribe/", unsubscribe_view, name="unsubscribe"),
    path("<int:pk>/~delete/", notification_delete_view, name="delete"),
    path("<int:pk>/~mark-read/", notification_mark_read_view, name="mark_read"),
    path("~delete-all/", notification_delete_all_view, name="delete_all"),
    path("~mark-all-read/", notification_mark_all_read_view, name="mark_all_read",),
]
