# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

from . import views

app_name = "invites"


urlpatterns = [
    path("", views.invite_list_view, name="list"),
    path("received/", views.received_invite_list_view, name="received_list"),
    path("~create/", views.invite_create_view, name="create"),
    path("<pk>/~resend/", views.invite_resend_view, name="resend"),
    path("<pk>/~delete/", views.invite_delete_view, name="delete"),
    path("<pk>/~accept/", views.invite_accept_view, name="accept"),
    path("<pk>/~reject/", views.invite_reject_view, name="reject"),
    path("<pk>/", views.invite_detail_view, name="detail"),
]
