from django.http import HttpRequest, HttpResponse

from communikit.types import get_response_callable


def _is_intercooler(self) -> bool:
    return self.is_ajax() and "x-ic-request" in self.headers


class IntercoolerRequestMiddleware:
    """
    Adds method `is_intercooler` to request instance if Intercooler
    headers are present and is an XHR request.

    Can be used inside views/templates etc thusly:
    ```
        if request.is_intercooler():
            # ....
    ```
    """

    def __init__(self, get_response: get_response_callable):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        request.is_intercooler = _is_intercooler.__get__(request)
        return self.get_response(request)


class IntercoolerRedirectMiddleware:
    """
    If Intercooler headers present then will send a 200 OK instead
    of redirect with IC redirect header.

    IntercoolerRequestMiddleware must be installed in MIDDLEWARE.
    """

    def __init__(self, get_response: get_response_callable):
        self.get_response = get_response

    def ic_response(self, response) -> HttpResponse:
        location = response["Location"]
        del response["Location"]
        ic_response = HttpResponse()
        for k, v in response.items():
            ic_response[k] = v
        ic_response["X-IC-Redirect"] = location
        return ic_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        response = self.get_response(request)
        if "Location" in response and request.is_intercooler():
            return self.ic_response(response)
        return response
