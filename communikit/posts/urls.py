# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from communikit.activities.views import create_activity_urls
from communikit.posts.forms import PostForm
from communikit.posts.models import Post

app_name = "posts"


urlpatterns = create_activity_urls(model=Post, form_class=PostForm)
