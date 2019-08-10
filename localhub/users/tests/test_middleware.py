# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.client import RequestFactory
from django.utils.encoding import force_text

from localhub.core.types import DjangoView
from localhub.users.middleware import UserLocaleMiddleware


class TestUserLocaleMiddleware:
    def test_set_language_in_cookie(
        self, req_factory: RequestFactory, get_response: DjangoView
    ):
        mw = UserLocaleMiddleware(get_response)
        req = req_factory.get("/")
        req.user = get_user_model()
        req.user.language = "fi"
        resp = mw(req)
        assert "django_language=fi" in force_text(
            resp.cookies[settings.LANGUAGE_COOKIE_NAME]
        )
