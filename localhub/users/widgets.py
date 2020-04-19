# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from localhub.forms.widgets import BaseTypeaheadInput

from .constants import MENTIONS_TYPEAHEAD_URL


class MentionsTypeaheadInput(BaseTypeaheadInput):
    typeahead_urls = (MENTIONS_TYPEAHEAD_URL,)
