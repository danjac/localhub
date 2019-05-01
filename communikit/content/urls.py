from django.urls import path

from communikit.content.views import (
    post_create_view,
    post_delete_view,
    post_detail_view,
    post_list_view,
    post_update_view,
)

app_name = "content"


urlpatterns = [
    path("", post_list_view, name="list"),
    path("~create/", post_create_view, name="create"),
    path("post/<int:pk>/", post_detail_view, name="detail"),
    path("post/<int:pk>/~update/", post_update_view, name="update"),
    path("post/<int:pk>/~delete/", post_delete_view, name="delete"),
]
