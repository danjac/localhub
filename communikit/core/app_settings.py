# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.urls import reverse_lazy

APP_PREFIX = "COMMUNIKIT_"

DEFAULT_PAGE_SIZE = getattr(settings, f"{APP_PREFIX}DEFAULT_PAGE_SIZE", 15)

HOME_PAGE_URL = getattr(
    settings, f"{APP_PREFIX}HOME_PAGE_URL", reverse_lazy("activities:stream")
)
