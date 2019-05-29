from django.urls import path

from communikit.posts.views import (
    post_create_view,
    post_delete_view,
    post_detail_view,
    post_dislike_view,
    post_like_view,
    post_list_view,
    post_notification_mark_read_view,
    post_update_view,
)

app_name = "posts"

urlpatterns = [
    path("", post_list_view, name="list"),
    path("~create", post_create_view, name="create"),
    path("<int:pk>/", post_detail_view, name="detail"),
    path("<int:pk>/~update/", post_update_view, name="update"),
    path("<int:pk>/~delete/", post_delete_view, name="delete"),
    path("<int:pk>/~like/", post_like_view, name="like"),
    path("<int:pk>/~dislike/", post_dislike_view, name="dislike"),
    path(
        "notifications/<int:pk>/~mark-read/",
        post_notification_mark_read_view,
        name="mark_notification_read",
    ),
]
