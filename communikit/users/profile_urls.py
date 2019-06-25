# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from communikit.activities.views import activity_profile_view
from communikit.comments.views import comment_profile_view
from communikit.users.views import user_detail_view

app_name = "profile"


urlpatterns = [
    path("<username>/comments/", view=comment_profile_view, name="comments"),
    path("<username>/posts/", view=activity_profile_view, name="activities"),
    path("<username>/", view=user_detail_view, name="detail"),
]
