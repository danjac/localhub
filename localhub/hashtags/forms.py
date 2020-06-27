# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


# Django
from django import forms

# Localhub
from localhub.forms.widgets import BaseTypeaheadInput

# Local
from .app_settings import HASHTAGS_TYPEAHEAD_CONFIG
from .validators import validate_hashtags


class HashtagsTypeaheadInput(BaseTypeaheadInput):
    typeahead_configs = [HASHTAGS_TYPEAHEAD_CONFIG]


class HashtagsField(forms.CharField):
    widget = HashtagsTypeaheadInput
    default_validators = [validate_hashtags]
