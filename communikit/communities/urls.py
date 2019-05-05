from django.urls import path

from communikit.communities.views import (
    community_update_view,
    membership_delete_view,
    membership_list_view,
    membership_update_view,
)

app_name = "communities"

urlpatterns = [
    path("~update/", view=community_update_view, name="community_update"),
    path("~memberships/", view=membership_list_view, name="membership_list"),
    path(
        "~memberships/<int:pk>/~update/",
        view=membership_update_view,
        name="membership_update",
    ),
    path(
        "~memberships/<int:pk>/~delete/",
        view=membership_delete_view,
        name="membership_delete",
    ),
]
