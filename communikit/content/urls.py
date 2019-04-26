from django.urls import path

from communikit.content.views import post_list_view

app_name = "content"


urlpatterns = [path("", post_list_view)]
