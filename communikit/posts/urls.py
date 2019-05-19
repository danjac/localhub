from django.urls import path

from communikit.posts.views import post_create_view

app_name = "posts"

urlpatterns = [path("~create", post_create_view, name="create")]
