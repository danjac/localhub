from django.urls import path

from communikit.activities.views import (
    activity_stream_view,
    activity_search_view,
)

app_name = "activities"

urlpatterns = [
    path("", activity_stream_view, name="stream"),
    path("search/", activity_search_view, name="search"),
]
