# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from localhub.subscriptions.views import (
    subscribed_user_list_view,
    subscribed_tag_list_view,
)

app_name = "subscriptions"


urlpatterns = [
    path("users/", view=subscribed_user_list_view, name="user_list"),
    path("tags/", view=subscribed_tag_list_view, name="tag_list"),
]
