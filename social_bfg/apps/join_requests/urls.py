# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.urls import path

from . import views

app_name = "join_requests"

urlpatterns = [
    path("", views.join_request_list_view, name="list"),
    path("sent/", views.sent_join_request_list_view, name="sent_list"),
    path("~create/", views.join_request_create_view, name="create"),
    path("<int:pk>/", views.join_request_detail_view, name="detail"),
    path("<int:pk>/~accept/", views.join_request_accept_view, name="accept"),
    path("<int:pk>/~reject/", views.join_request_reject_view, name="reject"),
    path("<int:pk>/~delete/", views.join_request_delete_view, name="delete"),
]
