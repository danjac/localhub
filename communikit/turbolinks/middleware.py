from django.http import HttpRequest, HttpResponse

from communikit.types import HttpRequestResponse


class TurbolinksMiddleware:

    session_key = "_turbolinks_redirect"
    location_header = "Turbolinks-Location"
    referrer_header = "Turbolinks-Referrer"

    def __init__(self, get_response: HttpRequestResponse):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:

        response = self.get_response(request)
        turbolinks_redirect = request.session.pop(self.session_key, None)

        if self.referrer_header in request.headers:

            if "Location" in response:
                location = response["Location"]
                if turbolinks_redirect and location.startswith("."):
                    location = turbolinks_redirect.split("?")[0] + location
                request.session[self.session_key] = location
            elif turbolinks_redirect:
                response[self.location_header] = turbolinks_redirect

        return response
