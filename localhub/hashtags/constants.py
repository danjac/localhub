
# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

import re

from django.urls import reverse_lazy

HASHTAGS_RE = re.compile(r"(?:^|\s)[＃#]{1}(\w+)")

HASHTAGS_TYPEAHEAD_URL = ("#", reverse_lazy("hashtags:autocomplete_list"))