# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from .views.actions import join_request_accept_view, join_request_reject_view
from .views.delete import join_request_delete_view
from .views.detail import join_request_detail_view
from .views.form import join_request_create_view
from .views.list import join_request_list_view, sent_join_request_list_view

app_name = "join_requests"

urlpatterns = [
    path("", view=join_request_list_view, name="list"),
    path("sent/", view=sent_join_request_list_view, name="sent_list"),
    path("~create/", view=join_request_create_view, name="create"),
    path("<int:pk>/", view=join_request_detail_view, name="detail"),
    path("<int:pk>/~accept/", view=join_request_accept_view, name="accept"),
    path("<int:pk>/~reject/", view=join_request_reject_view, name="reject"),
    path("<int:pk>/~delete/", view=join_request_delete_view, name="delete"),
]
