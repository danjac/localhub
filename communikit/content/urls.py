from django.urls import path

from communikit.content.views import (
    post_create_view,
    post_delete_view,
    post_detail_view,
    post_like_view,
    post_list_view,
    post_update_view,
    profile_post_list_view,
)

app_name = "content"


urlpatterns = [
    path("", post_list_view, name="list"),
    path("~create/", post_create_view, name="create"),
    path("profile/<username>/", profile_post_list_view, name="profile"),
    path("post/<int:pk>/", post_detail_view, name="detail"),
    path("post/<int:pk>/~update/", post_update_view, name="update"),
    path("post/<int:pk>/~delete/", post_delete_view, name="delete"),
    path("post/<int:pk>/~like/", post_like_view, name="like"),
]
