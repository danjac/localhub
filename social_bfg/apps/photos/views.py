# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings

# Social-BFG
from social_bfg.apps.activities.views.generic import BaseActivityListView

# Local
from .models import Photo


class PhotoGalleryView(BaseActivityListView):
    model = Photo
    template_name = "photos/gallery.html"
    paginate_by = settings.SOCIAL_BFG_DEFAULT_PAGE_SIZE

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
