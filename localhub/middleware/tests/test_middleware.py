# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponseRedirect

from .. import TurbolinksMiddleware


class TestTurbolinksMiddleware:
    def test_location_header(self, rf, get_response):
        mw = TurbolinksMiddleware(get_response)
        req = rf.get("/")
        req.session = {"_turbolinks_redirect": "/"}
        resp = mw(req)
        assert resp["Turbolinks-Location"] == "/"

    def test_handle_redirect_if_turbolinks(self, rf):
        def get_response(req):
            return HttpResponseRedirect("/")

        mw = TurbolinksMiddleware(get_response)
        req = rf.get(
            "/", HTTP_X_REQUESTED_WITH="XMLHttpRequest", HTTP_TURBOLINKS_REFERRER="/",
        )
        resp = mw(req)
        assert resp["Content-Type"] == "text/javascript"

    def test_handle_redirect_if_not_turbolinks(self, rf):
        def get_response(req):
            return HttpResponseRedirect("/")

        mw = TurbolinksMiddleware(get_response)
        req = rf.get("/")
        req.session = {}
        resp = mw(req)
        assert resp["Location"] == "/"
        assert req.session["_turbolinks_redirect"] == "/"
