# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.urls import path

from localhub.apps.activities.urls.generic import create_activity_urls

from .forms import PostForm
from .models import Post
from .views import opengraph_preview_view

app_name = "posts"


urlpatterns = create_activity_urls(Post, PostForm)
urlpatterns += [
    path("opengraph-preview/", opengraph_preview_view, name="opengraph_preview")
]
