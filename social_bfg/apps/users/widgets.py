# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django.conf import settings

# Social-BFG
from social_bfg.common.forms.widgets import BaseTypeaheadInput


class MentionsTypeaheadInput(BaseTypeaheadInput):
    typeahead_configs = [settings.SOCIAL_BFG_MENTIONS_TYPEAHEAD_CONFIG]
