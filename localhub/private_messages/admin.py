# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    raw_id_fields = ("sender", "recipient", "parent", "thread")
    readonly_fields = ("sender", "recipient", "parent", "thread", "message")
    ordering = ("-created",)
