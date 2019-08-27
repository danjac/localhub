# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings


class UserLocaleMiddleware:
    """
    Ensures the correct language cookie is set in the response
    depending on the user's lang preference.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.user.is_authenticated:
            response.set_cookie(
                settings.LANGUAGE_COOKIE_NAME, request.user.language
            )
        return response
