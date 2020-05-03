# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.notification_list_view, name="list"),
    path("service-worker.js", views.service_worker_view, name="service_worker"),
    path("~subscribe/", views.subscribe_view, name="subscribe"),
    path("~unsubscribe/", views.unsubscribe_view, name="unsubscribe"),
    path("<int:pk>/~delete/", views.notification_delete_view, name="delete"),
    path("<int:pk>/~mark-read/", views.notification_mark_read_view, name="mark_read"),
    path("~delete-all/", views.notification_delete_all_view, name="delete_all"),
    path(
        "~mark-all-read/", views.notification_mark_all_read_view, name="mark_all_read",
    ),
]
