# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localhub.activities.views import create_activity_urls

from .forms import PostForm
from .models import Post

app_name = "posts"


urlpatterns = create_activity_urls(Post, PostForm)
