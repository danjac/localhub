# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import path

from localhub.activities.urls.generic import create_activity_urls

from .forms import PhotoForm
from .models import Photo
from .views import photo_gallery_view

app_name = "photos"


urlpatterns = create_activity_urls(Photo, PhotoForm)

urlpatterns += [path("gallery/", photo_gallery_view, name="gallery")]
