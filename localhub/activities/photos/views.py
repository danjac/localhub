# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Localhub
from localhub.common.pagination import render_paginated_queryset
from localhub.communities.decorators import community_required

# Local
from .models import Photo


@community_required
def photo_gallery_view(request):
    photos = (
        Photo.objects.for_community(request.community)
        .published_or_owner(request.user)
        .exclude_blocked(request.user)
        .filter(parent__isnull=True)
        .order_by("-created", "-published")
    )
    return render_paginated_queryset(request, photos, "photos/gallery.html")
