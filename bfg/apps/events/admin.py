# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from bfg.apps.activities.admin import ActivityAdmin

from .models import Event


@admin.register(Event)
class EventAdmin(ActivityAdmin):
    ...