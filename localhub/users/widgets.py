# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Localhub
from localhub.common.forms.widgets import BaseTypeaheadInput

# Local
from .app_settings import MENTIONS_TYPEAHEAD_CONFIG


class MentionsTypeaheadInput(BaseTypeaheadInput):
    typeahead_configs = [MENTIONS_TYPEAHEAD_CONFIG]
