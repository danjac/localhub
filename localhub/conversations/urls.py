from django.urls import path


from localhub.conversations.views import (
    conversation_view,
    inbox_view,
    message_create_view,
    message_delete_view,
    message_detail_view,
    message_mark_read_view,
    message_reply_view,
    outbox_view,
)

app_name = "conversations"

urlpatterns = [
    path("", inbox_view, name="inbox"),
    path("outbox/", outbox_view, name="outbox"),
    path("user/<slug:slug>/", conversation_view, name="conversation"),
    path(
        "user/<slug:slug>/~send/", message_create_view, name="message_create"
    ),
    path("message/<int:pk>/", message_detail_view, name="message_detail"),
    path("message/<int:pk>/~reply/", message_reply_view, name="message_reply"),
    path(
        "message/<int:pk>/~delete/", message_delete_view, name="message_delete"
    ),
    path(
        "message/<int:pk>/~read/",
        message_mark_read_view,
        name="message_mark_read",
    ),
]
