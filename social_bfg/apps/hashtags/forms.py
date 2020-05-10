# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django import forms
from django.conf import settings

# Social-BFG
from social_bfg.common.forms.widgets import BaseTypeaheadInput

# Local
from .validators import validate_hashtags


class HashtagsTypeaheadInput(BaseTypeaheadInput):
    typeahead_configs = [settings.SOCIAL_BFG_HASHTAGS_TYPEAHEAD_CONFIG]


class HashtagsField(forms.CharField):
    widget = HashtagsTypeaheadInput
    default_validators = [validate_hashtags]
