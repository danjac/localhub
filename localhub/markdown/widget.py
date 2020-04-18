# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.urls import reverse_lazy

from markdownx.widgets import MarkdownxWidget

from localhub.forms.widgets import TypeaheadMixin

# TBD: these will get moved to individual constants modules
HASHTAGS_URL = ("#", reverse_lazy("hashtags:autocomplete_list"))
MENTIONS_URL = ("@", reverse_lazy("users:autocomplete_list"))


class TypeaheadMarkdownWidget(TypeaheadMixin, MarkdownxWidget):
    ...
    typeahead_urls = (HASHTAGS_URL, MENTIONS_URL)
