# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localite.activities.views import create_activity_urls
from localite.posts.forms import PostForm
from localite.posts.models import Post

app_name = "posts"


urlpatterns = create_activity_urls(Post, PostForm)
