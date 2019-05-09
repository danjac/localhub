from django.urls import path

from communikit.invites.views import invite_list_view, invite_create_view

app_name = "invites"


urlpatterns = [
    path("", view=invite_list_view, name="list"),
    path("~create/", view=invite_create_view, name="create"),
]
