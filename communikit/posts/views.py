# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from communikit.activities.views import (
    ActivityCreateView,
    ActivityDeleteView,
    ActivityDetailView,
    ActivityDislikeView,
    ActivityLikeView,
    ActivityListView,
    ActivityUpdateView,
)
from communikit.posts.forms import PostForm
from communikit.posts.models import Post


post_create_view = ActivityCreateView.as_view(model=Post, form_class=PostForm)

post_list_view = ActivityListView.as_view(model=Post)

post_detail_view = ActivityDetailView.as_view(model=Post)

post_update_view = ActivityUpdateView.as_view(model=Post, form_class=PostForm)

post_delete_view = ActivityDeleteView.as_view(model=Post)

post_like_view = ActivityLikeView.as_view(model=Post)

post_dislike_view = ActivityDislikeView.as_view(model=Post)
