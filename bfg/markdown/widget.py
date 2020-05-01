# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings

from markdownx.widgets import MarkdownxWidget

from bfg.forms.widgets import TypeaheadMixin


class TypeaheadMarkdownWidget(TypeaheadMixin, MarkdownxWidget):
    typeahead_configs = (
        settings.BFG_HASHTAGS_TYPEAHEAD_CONFIG,
        settings.BFG_MENTIONS_TYPEAHEAD_CONFIG,
    )
