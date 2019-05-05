from django.urls import path

from communikit.communities.views import community_update_view

app_name = "communities"

urlpatterns = [path("~update/", view=community_update_view, name="update")]
