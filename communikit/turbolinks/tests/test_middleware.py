from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.test.client import RequestFactory

from communikit.turbolinks.middleware import TurbolinksMiddleware
from communikit.types import HttpRequestResponse


class TestTurbolinksMiddleware:
    def test_location_header(
        self, req_factory: RequestFactory, get_response: HttpRequestResponse
    ):
        mw = TurbolinksMiddleware(get_response)
        req = req_factory.get("/")
        req.session = {"_turbolinks_redirect": "/"}
        resp = mw(req)
        assert resp["Turbolinks-Location"] == "/"

    def test_handle_redirect_if_turbolinks(self, req_factory: RequestFactory):
        def get_response(req: HttpRequest) -> HttpResponse:
            return HttpResponseRedirect("/")

        mw = TurbolinksMiddleware(get_response)
        req = req_factory.get(
            "/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_TURBOLINKS_REFERRER="/",
        )
        resp = mw(req)
        assert resp["Content-Type"] == "text/javascript"

    def test_handle_redirect_if_not_turbolinks(
        self, req_factory: RequestFactory
    ):
        def get_response(req: HttpRequest) -> HttpResponse:
            return HttpResponseRedirect("/")

        mw = TurbolinksMiddleware(get_response)
        req = req_factory.get("/")
        req.session = {}
        resp = mw(req)
        assert resp["Location"] == "/"
        assert req.session["_turbolinks_redirect"] == "/"
