# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from . import views

app_name = "communities"

urlpatterns = [
    path("about/", views.community_detail_view, name="community_detail"),
    path("terms/", views.community_terms_view, name="community_terms"),
    path("~update/", views.community_update_view, name="community_update"),
    path("~leave/", views.membership_leave_view, name="membership_leave"),
    path("memberships/", views.membership_list_view, name="membership_list"),
    path(
        "memberships/<int:pk>/", views.membership_detail_view, name="membership_detail",
    ),
    path(
        "memberships/<int:pk>/~update/",
        views.membership_update_view,
        name="membership_update",
    ),
    path(
        "memberships/<int:pk>/~delete/",
        views.membership_delete_view,
        name="membership_delete",
    ),
]
