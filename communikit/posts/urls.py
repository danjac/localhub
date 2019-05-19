from django.urls import path

from communikit.posts.views import post_create_view, post_detail_view

app_name = "posts"

urlpatterns = [
    path("~create", post_create_view, name="create"),
    path("<int:pk>/", post_detail_view, name="detail"),
]
