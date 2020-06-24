# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Global constants

# Django
from django.urls import reverse_lazy

DEFAULT_PAGE_SIZE = 12
LONG_PAGE_SIZE = 24

HOME_PAGE_URL = reverse_lazy("activity_stream")
