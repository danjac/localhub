# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views import (
    invite_accept_view,
    invite_create_view,
    invite_delete_view,
    invite_list_view,
    invite_resend_view,
)

app_name = "invites"


urlpatterns = [
    path("", view=invite_list_view, name="list"),
    path("~create/", view=invite_create_view, name="create"),
    path("<pk>/~resend/", view=invite_resend_view, name="resend"),
    path("<pk>/~delete/", view=invite_delete_view, name="delete"),
    path("<pk>/~accept/", view=invite_accept_view, name="accept"),
]
