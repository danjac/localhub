# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path, re_path

from localhub.apps.users.urls import USERNAME_RE

from .views.actions import (
    message_bookmark_view,
    message_delete_view,
    message_mark_all_read_view,
    message_mark_read_view,
    message_remove_bookmark_view,
)
from .views.create import (
    message_create_view,
    message_follow_up_view,
    message_recipient_create_view,
    message_reply_view,
)
from .views.list_detail import inbox_view, message_detail_view, outbox_view

app_name = "private_messages"

urlpatterns = [
    path("inbox/", inbox_view, name="inbox"),
    path("outbox/", outbox_view, name="outbox"),
    path("send/", message_create_view, name="message_create"),
    path("~/mark-read/", message_mark_all_read_view, name="mark_all_read"),
    path("message/<int:pk>/", message_detail_view, name="message_detail"),
    path(
        "message/<int:pk>/~follow-up/", message_follow_up_view, name="message_follow_up"
    ),
    path("message/<int:pk>/~reply/", message_reply_view, name="message_reply"),
    path("message/<int:pk>/~delete/", message_delete_view, name="message_delete"),
    path("message/<int:pk>/~read/", message_mark_read_view, name="message_mark_read"),
    path(
        "message/<int:pk>/~bookmark/", message_bookmark_view, name="message_bookmark",
    ),
    path(
        "message/<int:pk>/~bookmark/remove/",
        message_remove_bookmark_view,
        name="message_remove_bookmark",
    ),
    re_path(
        USERNAME_RE + r"~send/$",
        message_recipient_create_view,
        name="message_create_recipient",
    ),
]
