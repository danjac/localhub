# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.contrib import admin

# Local
from .models import JoinRequest


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    raw_id_fields = ("sender",)
    list_display = ("sender", "community", "status")
    ordering = ("-sent",)
