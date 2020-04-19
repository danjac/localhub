# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later


from django import forms

from localhub.forms.widgets import BaseTypeaheadInput

from .constants import HASHTAGS_TYPEAHEAD_URL


class HashtagsTypeaheadInput(BaseTypeaheadInput):
    typeahead_urls = (HASHTAGS_TYPEAHEAD_URL,)


class HashtagsFormField(forms.CharField):
    widget = HashtagsTypeaheadInput
