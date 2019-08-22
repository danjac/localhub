from django.urls import path


from localhub.conversations.views import (
    conversation_view,
    inbox_view,
    message_create_view,
    message_delete_view,
    message_detail_view,
    message_mark_read_view,
    outbox_view,
)

app_name = "conversations"

urlpatterns = [
    path("", inbox_view, name="inbox"),
    path("outbox/", outbox_view, name="outbox"),
    path("<slug:slug>/", conversation_view, name="conversation"),
    path("<slug:slug>/~send/", message_create_view, name="message_create"),
    path("messages/<int:pk>/", message_detail_view, name="message_detail"),
    path(
        "messages/<int:pk>/~delete/",
        message_delete_view,
        name="message_delete",
    ),
    path(
        "messages/<int:pk>/~read/",
        message_mark_read_view,
        name="message_mark_read",
    ),
]
