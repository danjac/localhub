# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpRequest

from ..context_processors import theme


class TestDarkmode:
    def test_default(self):
        req = HttpRequest()
        req.COOKIES = {}
        assert theme(req) == {"theme": "light"}

    def test_dark_theme(self):
        req = HttpRequest()
        req.COOKIES = {"theme": "dark"}
        assert theme(req) == {"theme": "dark"}
