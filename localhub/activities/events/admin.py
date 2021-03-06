# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib import admin

# Localhub
from localhub.activities.admin import ActivityAdmin

# Local
from .models import Event


@admin.register(Event)
class EventAdmin(ActivityAdmin):
    ...
