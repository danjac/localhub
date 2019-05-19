from django.urls import path

from communikit.posts.views import (
    post_create_view,
    post_detail_view,
    post_update_view,
)

app_name = "posts"

urlpatterns = [
    path("~create", post_create_view, name="create"),
    path("<int:pk>/", post_detail_view, name="detail"),
    path("<int:pk>/~update/", post_update_view, name="update"),
]
