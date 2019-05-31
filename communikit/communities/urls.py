from django.urls import path

from communikit.communities.views import (
    community_membership_list_view,
    community_update_view,
    membership_delete_view,
    membership_update_view,
    user_membership_list_view,
)

app_name = "communities"

urlpatterns = [
    path("~update/", view=community_update_view, name="community_update"),
    path(
        "communities/",
        view=user_membership_list_view,
        name="user_membership_list",
    ),
    path(
        "memberships/",
        view=community_membership_list_view,
        name="community_membership_list",
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
