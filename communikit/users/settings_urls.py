# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from communikit.users.views import user_update_view, user_delete_view


app_name = "settings"


urlpatterns = [
    path("~update/", view=user_update_view, name="update"),
    path("~delete/", view=user_delete_view, name="delete"),
]
