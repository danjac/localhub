# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils import timezone


class TimezoneOverrideMixin:
    """Ensures timezone is localized to user preference"""

    def dispatch(self, request, *args, **kwargs):
        with timezone.override(
            request.user.default_timezone if request.user.is_authenticated else None
        ):
            return super().dispatch(request, *args, **kwargs)
