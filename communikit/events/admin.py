# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from communikit.activities.admin import ActivityAdmin
from communikit.events.models import Event


@admin.register(Event)
class EventAdmin(ActivityAdmin):
    ...
