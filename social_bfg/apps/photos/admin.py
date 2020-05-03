# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from social_bfg.apps.activities.admin import ActivityAdmin
from sorl.thumbnail.admin import AdminImageMixin

from .models import Photo


@admin.register(Photo)
class PhotoAdmin(AdminImageMixin, ActivityAdmin):
    ...
