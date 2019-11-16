# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin
from sorl.thumbnail.admin import AdminImageMixin

from localhub.activities.admin import ActivityAdmin
from localhub.photos.models import Photo


@admin.register(Photo)
class PhotoAdmin(AdminImageMixin, ActivityAdmin):
    ...
