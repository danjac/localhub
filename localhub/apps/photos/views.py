# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Localhub
from localhub.apps.activities.views.generic import BaseActivityListView
from localhub.config.app_settings import DEFAULT_PAGE_SIZE

# Local
from .models import Photo


class PhotoGalleryView(BaseActivityListView):
    model = Photo
    template_name = "photos/gallery.html"
    paginate_by = DEFAULT_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .published_or_owner(self.request.user)
            .exclude_blocked(self.request.user)
            .filter(parent__isnull=True)
            .order_by("-created", "-published")
        )


photo_gallery_view = PhotoGalleryView.as_view()
