# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path, re_path

# Social-BFG
from social_bfg.apps.users.urls import USERNAME_RE

# Local
from . import views

app_name = "private_messages"

urlpatterns = [
    path("inbox/", views.inbox_view, name="inbox"),
    path("outbox/", views.outbox_view, name="outbox"),
    path("send/", views.message_create_view, name="message_create"),
    path("~/mark-read/", views.message_mark_all_read_view, name="mark_all_read"),
    path("message/<int:pk>/", views.message_detail_view, name="message_detail"),
    path(
        "message/<int:pk>/~follow-up/",
        views.message_follow_up_view,
        name="message_follow_up",
    ),
    path("message/<int:pk>/~reply/", views.message_reply_view, name="message_reply"),
    path("message/<int:pk>/~delete/", views.message_delete_view, name="message_delete"),
    path(
        "message/<int:pk>/~read/",
        views.message_mark_read_view,
        name="message_mark_read",
    ),
    path(
        "message/<int:pk>/~bookmark/",
        views.message_bookmark_view,
        name="message_bookmark",
    ),
    path(
        "message/<int:pk>/~bookmark/remove/",
        views.message_remove_bookmark_view,
        name="message_remove_bookmark",
    ),
    re_path(
        USERNAME_RE + r"~send/$",
        views.message_recipient_create_view,
        name="message_create_recipient",
    ),
]
