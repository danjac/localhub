from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.test.client import RequestFactory

from communikit.turbolinks.middleware import TurbolinksMiddleware


class TestTurbolinksMiddleware:
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
