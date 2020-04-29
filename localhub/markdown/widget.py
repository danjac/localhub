# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings

from markdownx.widgets import MarkdownxWidget

from localhub.forms.widgets import TypeaheadMixin


class TypeaheadMarkdownWidget(TypeaheadMixin, MarkdownxWidget):
    typeahead_urls = (
        settings.LOCALHUB_HASHTAGS_TYPEAHEAD_URL,
        settings.LOCALHUB_MENTIONS_TYPEAHEAD_URL,
    )
