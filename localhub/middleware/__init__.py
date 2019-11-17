# Copyright (c) 2019 by Dan Jacob
# SPDX-License-Identifier: AGPL-3.0-or-later

from django.http import HttpResponse


class DoNotTrackMiddleware:
    """
    Checks if DoNotTrack(DNT) HTTP header is present.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.do_not_track = request.headers.get("DNT") == "1"
        return self.get_response(request)


class TurbolinksMiddleware:
    """
    This provides backend Django complement to the Turbolinks JS framework:

    https://github.com/turbolinks/turbolinks

    In particular redirects are handled correctly as per the documentation.
    """

    session_key = "_turbolinks_redirect"
    location_header = "Turbolinks-Location"
    referrer_header = "Turbolinks-Referrer"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        response = self.get_response(request)
        if response.status_code in (301, 302) and response.has_header("Location"):
            return self.handle_redirect(request, response)
        if response.status_code in range(200, 299):
            location = request.session.pop(self.session_key, None)
            if location:
                response[self.location_header] = location
        return response

    def handle_redirect(self, request, response):
        if self.is_turbolinks_request(request):
            return self.redirect_with_turbolinks(request, response)
        request.session[self.session_key] = response["Location"]
        return response

    def is_turbolinks_request(self, request):
        return request.is_ajax() and self.referrer_header in request.headers

    def redirect_with_turbolinks(self, request, response):
        js = []
        if request.method not in ("GET", "HEAD", "OPTIONS", "TRACE"):
            js.append("Turbolinks.clearCache();")
        js.append("Turbolinks.visit('{}');".format(response["Location"]))
        js_response = HttpResponse("\n".join(js), content_type="text/javascript")
        # make sure we pass down any cookies e.g. for handling messages
        for k, v in response.cookies.items():
            js_response.set_cookie(k, v)
        return js_response
