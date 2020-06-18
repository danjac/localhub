# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings

# Third Party Libraries
from markdownx.widgets import MarkdownxWidget

# Localhub
from localhub.forms.widgets import TypeaheadMixin


class TypeaheadMarkdownWidget(TypeaheadMixin, MarkdownxWidget):
    typeahead_configs = (
        settings.LOCALHUB_HASHTAGS_TYPEAHEAD_CONFIG,
        settings.LOCALHUB_MENTIONS_TYPEAHEAD_CONFIG,
    )
