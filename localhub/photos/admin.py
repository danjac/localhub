# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib import admin

# Third Party Libraries
from sorl.thumbnail.admin import AdminImageMixin

# Localhub
from localhub.activities.admin import ActivityAdmin

# Local
from .models import Photo


@admin.register(Photo)
class PhotoAdmin(AdminImageMixin, ActivityAdmin):
    ...
