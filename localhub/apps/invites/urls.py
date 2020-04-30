# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views.actions import invite_accept_view, invite_reject_view, invite_resend_view
from .views.create import invite_create_view
from .views.delete import invite_delete_view
from .views.detail import invite_detail_view
from .views.list import invite_list_view, received_invite_list_view

app_name = "invites"


urlpatterns = [
    path("", view=invite_list_view, name="list"),
    path("received/", view=received_invite_list_view, name="received_list"),
    path("~create/", view=invite_create_view, name="create"),
    path("<pk>/~resend/", view=invite_resend_view, name="resend"),
    path("<pk>/~delete/", view=invite_delete_view, name="delete"),
    path("<pk>/~accept/", view=invite_accept_view, name="accept"),
    path("<pk>/~reject/", view=invite_reject_view, name="reject"),
    path("<pk>/", view=invite_detail_view, name="detail"),
]
