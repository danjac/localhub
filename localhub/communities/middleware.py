# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.utils.functional import SimpleLazyObject

# Local
from .models import Community


class CurrentCommunityMiddleware:
    """
    Lazily fetches the current community matching the domain
    and appends to the request object as `community`.

    If no community found this value will be *None*.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.community = SimpleLazyObject(
            lambda: Community.objects.get_current(request)
        )
        return self.get_response(request)
