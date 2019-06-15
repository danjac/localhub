from django.urls import path

from communikit.users.views import (
    user_detail_view,
    user_update_view,
    user_delete_view,
)


app_name = "users"


urlpatterns = [
    path("~update/", view=user_update_view, name="update"),
    path("~delete/", view=user_delete_view, name="delete"),
    path("<username>/", view=user_detail_view, name="detail"),
]
