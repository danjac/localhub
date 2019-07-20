# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from simple_history.admin import SimpleHistoryAdmin

from localhub.core.markdown.admin import MarkdownFieldMixin


class ActivityAdmin(MarkdownFieldMixin, SimpleHistoryAdmin):
    raw_id_fields = ("owner",)
    list_display = ("__str__", "owner", "community", "created")
    ordering = ("-created",)
