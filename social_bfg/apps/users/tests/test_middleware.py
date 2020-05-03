# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

# Django
from django.conf import settings
from django.utils.encoding import force_text

from ..middleware import UserLocaleMiddleware


class TestUserLocaleMiddleware:
    def test_set_language_in_cookie(self, rf, get_response, user_model):
        mw = UserLocaleMiddleware(get_response)
        req = rf.get("/")
        req.user = user_model()
        req.user.language = "fi"
        resp = mw(req)
        assert "django_language=fi" in force_text(
            resp.cookies[settings.LANGUAGE_COOKIE_NAME]
        )
