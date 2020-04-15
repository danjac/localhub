# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings

from localhub.activities.views.list import BaseActivityListView

from .models import Photo


class PhotoGalleryView(BaseActivityListView):
    model = Photo
    template_name = "photos/gallery.html"
    paginate_by = settings.LOCALHUB_LONG_PAGE_SIZE

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .published()
            .exclude_blocked(self.request.user)
            .order_by("-published")
        )


photo_gallery_view = PhotoGalleryView.as_view()
