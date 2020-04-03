# Copyright (c) 2020 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpRequest

from ..context_processors import darkmode


class TestDarkmode:
    def test_is_darkmode(self):
        req = HttpRequest()
        req.COOKIES = {"darkmode": "1"}
        assert darkmode(req) == {"darkmode": True}

    def test_is_not_darkmode(self):
        req = HttpRequest()
        req.COOKIES = {}
        assert darkmode(req) == {"darkmode": False}
