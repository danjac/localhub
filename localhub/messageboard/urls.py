from django.urls import path

from localhub.messageboard.views import (
    message_create_view,
    message_detail_view,
    message_list_view,
    message_recipient_delete_view,
    message_recipient_detail_view,
    message_recipient_list_view,
)

app_name = "messageboard"

urlpatterns = [
    path("", message_recipient_list_view, name="message_recipient_list"),
    path(
        "inbox/<int:pk>/",
        message_recipient_detail_view,
        name="message_recipient_detail",
    ),
    path(
        "inbox/<int:pk>/~delete/",
        message_recipient_delete_view,
        name="message_recipient_delete",
    ),
    path("outbox/", message_list_view, name="message_list"),
    path("outbox/<int:pk>/", message_detail_view, name="message_detail"),
    path("new/", message_create_view, name="message_create"),
    path(
        "reply/<int:parent>/", message_create_view, name="message_create_reply"
    ),
    path("pm/<slug:username>/", message_create_view, name="message_create_pm"),
]
