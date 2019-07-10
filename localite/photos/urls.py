# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localite.activities.views import create_activity_urls
from localite.photos.forms import PhotoForm
from localite.photos.models import Photo

app_name = "photos"


urlpatterns = create_activity_urls(Photo, PhotoForm)
