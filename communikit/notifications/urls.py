from django.urls import path

from communikit.notifications.views import (
    notification_mark_read_view,
    notification_list_view,
)

app_name = "notifications"

urlpatterns = [
    path("", notification_list_view, name="list"),
    path(
        "<int:pk>/~mark-read/",
        notification_mark_read_view,
        name="mark_notification_read",
    ),
]
