# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Standard Library
import functools

# Django
from django.utils import timezone


def override_timezone(view):
    @functools.wraps(view)
    def wrapper(request, *args, **kwargs):
        with timezone.override(
            request.user.default_timezone if request.user.is_authenticated else None
        ):

            return view(request, *args, **kwargs)

    return wrapper
