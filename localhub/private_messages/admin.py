# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):

    readonly_fields = (
        "sender",
        "recipient",
        "parent",
        "message",
        "community",
        "read",
    )
    list_display = ("sender", "recipient", "created")
    search_fields = (
        "search_document",
        "recipient__username",
        "sender__username",
    )
    ordering = ("-created",)
