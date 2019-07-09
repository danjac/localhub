from django.http import HttpRequest, HttpResponse

from communikit.core.types import DjangoView


class TurbolinksMiddleware:
    """
    This provides backend Django complement to the Turbolinks JS framework:

    https://github.com/turbolinks/turbolinks

    In particular redirects are handled correctly as per the documentation.
    """

    session_key = "_turbolinks_redirect"
    location_header = "Turbolinks-Location"
    referrer_header = "Turbolinks-Referrer"

    def __init__(self, get_response: DjangoView):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:

        response = self.get_response(request)
        if response.status_code in (301, 302) and response.has_header(
            "Location"
        ):
            return self.handle_redirect(request, response)
        if response.status_code in range(200, 299):
            location = request.session.pop(self.session_key, None)
            if location:
                response[self.location_header] = location
        return response

    def handle_redirect(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        if self.is_turbolinks_request(request):
            return self.redirect_with_turbolinks(request, response)
        request.session[self.session_key] = response["Location"]
        return response

    def is_turbolinks_request(self, request: HttpRequest) -> bool:
        return request.is_ajax() and self.referrer_header in request.headers

    def redirect_with_turbolinks(
        self, request: HttpRequest, response: HttpResponse
    ) -> HttpResponse:
        js = []
        if request.method not in ("GET", "HEAD", "OPTIONS", "TRACE"):
            js.append("Turbolinks.clearCache();")
        js.append("Turbolinks.visit('{}');".format(response["Location"]))
        js_response = HttpResponse(
            "\n".join(js), content_type="text/javascript"
        )
        # make sure we pass down any cookies e.g. for handling messages
        for k, v in response.cookies.items():
            js_response.set_cookie(k, v)
        return js_response
