# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import reverse_lazy

DEFAULT_PAGE_SIZE = getattr(settings, "COMMUNIKIT_DEFAULT_PAGE_SIZE", 15)

HOME_PAGE_URL = getattr(
    settings, "COMMUNIKIT_HOME_PAGE_URL", reverse_lazy("activities:stream")
)
