from django.urls import path

from communikit.notifications.views import NotificationMarkReadView
from communikit.posts.models import PostNotification
from communikit.posts.views import (
    post_create_view,
    post_delete_view,
    post_detail_view,
    post_dislike_view,
    post_like_view,
    post_update_view,
)

app_name = "posts"

urlpatterns = [
    path("~create", post_create_view, name="create"),
    path("<int:pk>/", post_detail_view, name="detail"),
    path("<int:pk>/~update/", post_update_view, name="update"),
    path("<int:pk>/~delete/", post_delete_view, name="delete"),
    path("<int:pk>/~like/", post_like_view, name="like"),
    path("<int:pk>/~dislike/", post_dislike_view, name="dislike"),
    path(
        "notifications/<int:pk>/~mark-read/",
        NotificationMarkReadView.as_view(model=PostNotification),
        name="mark_notification_read",
    ),
]
