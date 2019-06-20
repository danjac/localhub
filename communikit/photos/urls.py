# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from communikit.activities.views import ActivityViewSet
from communikit.photos.forms import PhotoForm
from communikit.photos.models import Photo

app_name = "photos"


urlpatterns = ActivityViewSet(model=Photo, form_class=PhotoForm).urls
