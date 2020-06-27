# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Third Party Libraries
from markdownx.widgets import MarkdownxWidget

# Localhub
from localhub.forms.widgets import TypeaheadMixin
from localhub.hashtags.app_settings import HASHTAGS_TYPEAHEAD_CONFIG
from localhub.users.app_settings import MENTIONS_TYPEAHEAD_CONFIG


class TypeaheadMarkdownWidget(TypeaheadMixin, MarkdownxWidget):
    typeahead_configs = (
        HASHTAGS_TYPEAHEAD_CONFIG,
        MENTIONS_TYPEAHEAD_CONFIG,
    )
