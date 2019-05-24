# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings

DEFAULT_PAGE_SIZE = getattr(
    settings, "COMMUNIKIT_DEFAULT_PAGE_SIZE", 15
)
