# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from communikit.communities.views import (
    community_list_view,
    community_update_view,
    membership_delete_view,
    community_leave_view,
    membership_list_view,
    membership_update_view,
)

app_name = "communities"

urlpatterns = [
    path("~update/", view=community_update_view, name="community_update"),
    path("communities/", view=community_list_view, name="community_list"),
    path("memberships/", view=membership_list_view, name="membership_list"),
    path("leave/", view=community_leave_view, name="leave"),
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
