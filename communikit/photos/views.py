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
from communikit.photos.forms import PhotoForm
from communikit.photos.models import Photo


photo_create_view = ActivityCreateView.as_view(
    model=Photo, form_class=PhotoForm
)

photo_list_view = ActivityListView.as_view(model=Photo)

photo_detail_view = ActivityDetailView.as_view(model=Photo)

photo_update_view = ActivityUpdateView.as_view(
    model=Photo, form_class=PhotoForm
)

photo_delete_view = ActivityDeleteView.as_view(model=Photo)

photo_like_view = ActivityLikeView.as_view(model=Photo)

photo_dislike_view = ActivityDislikeView.as_view(model=Photo)
