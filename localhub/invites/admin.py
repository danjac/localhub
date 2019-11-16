# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from .models import Invite


@admin.register(Invite)
class InviteAdmin(admin.ModelAdmin):
    raw_id_fields = ("sender",)
    list_display = ("email", "sender", "community", "status")
    ordering = ("-sent",)
