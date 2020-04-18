# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from markdownx.widgets import MarkdownxWidget

from localhub.forms.widgets import TypeaheadMixin
from localhub.hashtags.constants import HASHTAGS_TYPEAHEAD_URL
from localhub.users.constants import MENTIONS_TYPEAHEAD_URL


class TypeaheadMarkdownWidget(TypeaheadMixin, MarkdownxWidget):
    typeahead_urls = (HASHTAGS_TYPEAHEAD_URL, MENTIONS_TYPEAHEAD_URL)
