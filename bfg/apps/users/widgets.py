# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django.conf import settings

from bfg.forms.widgets import BaseTypeaheadInput


class MentionsTypeaheadInput(BaseTypeaheadInput):
    typeahead_configs = [settings.BFG_MENTIONS_TYPEAHEAD_CONFIG]
