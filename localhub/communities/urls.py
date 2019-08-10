# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from localhub.communities.views import (
    community_detail_view,
    community_leave_view,
    community_terms_view,
    community_update_view,
    membership_delete_view,
    membership_detail_view,
    membership_list_view,
    membership_update_view,
)

app_name = "communities"

urlpatterns = [

    path("", view=community_detail_view, name="community_detail"),
    path("terms/", view=community_terms_view, name="community_terms"),
    path("~leave/", view=community_leave_view, name="leave"),
    path("~update/", view=community_update_view, name="community_update"),

    path("memberships/", view=membership_list_view, name="membership_list"),
    path(
        "memberships/<int:pk>/",
        view=membership_detail_view,
        name="membership_detail",
    ),
    path(
        "memberships/<int:pk>/~update/",
        view=membership_update_view,
        name="membership_update",
    ),
    path(
        "memberships/<int:pk>/~delete/",
        view=membership_delete_view,
        name="membership_delete",
    ),
]
