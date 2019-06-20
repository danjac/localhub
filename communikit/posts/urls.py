# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from communikit.activities.views import ActivityViewSet
from communikit.posts.forms import PostForm
from communikit.posts.models import Post

app_name = "posts"


urlpatterns = ActivityViewSet(model=Post, form_class=PostForm).urls
