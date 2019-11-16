# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpRequest, HttpResponseRedirect

from localhub.common.middleware import (
    DoNotTrackMiddleware,
    TurbolinksMiddleware,
)


class TestDoNotTrackMiddleware:
    def test_if_header_present(self, rf, get_response):
        mw = DoNotTrackMiddleware(get_response)
        req = rf.get("/", HTTP_DNT="1")
        mw(req)
        assert req.do_not_track

    def test_if_header_not_present(self, rf, get_response):
        mw = DoNotTrackMiddleware(get_response)
        req = rf.get("/")
        mw(req)
        assert not req.do_not_track


class TestTurbolinksMiddleware:
    def test_location_header(self, rf, get_response):
        mw = TurbolinksMiddleware(get_response)
        req = rf.get("/")
        req.session = {"_turbolinks_redirect": "/"}
        resp = mw(req)
        assert resp["Turbolinks-Location"] == "/"

    def test_handle_redirect_if_turbolinks(self, rf):
        def get_response(req: HttpRequest):
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
