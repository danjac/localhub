# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from communikit.activities.views import create_activity_urls
from communikit.photos.forms import PhotoForm
from communikit.photos.models import Photo

app_name = "photos"


urlpatterns = create_activity_urls(model=Photo, form_class=PhotoForm)
