from django.urls import path

from communikit.content.views import (
    post_list_view,
    post_create_view,
    post_detail_view,
)

app_name = "content"


urlpatterns = [
    path("", post_list_view, name="list"),
    path("new/", post_create_view, name="create"),
    path("post/<int:pk>/", post_detail_view, name="detail"),
]
