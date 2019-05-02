from typing import Dict, Optional

from django.http import HttpRequest, HttpResponse, QueryDict
from django.utils.functional import SimpleLazyObject

from communikit.types import get_response_callable

INTERCOOLER_PARAMS = (
    "ic-request",
    "ic-trigger-id",
    "ic-element-id",
    "ic-element-name",
    "ic-target-id",
    "ic-trigger-name",
    "ic-current-url",
    "ic-prompt-value",
)


class IntercoolerData:
    def __init__(self, params: Dict[str, str]):
        self.params = params

    @property
    def request(self) -> bool:
        return "ic-request" in self.params

    @property
    def target_id(self) -> Optional[str]:
        return self.params.get("ic-target-id")

    @property
    def current_url(self) -> Optional[str]:
        return self.params.get("ic-current_url")

    @property
    def element_id(self) -> Optional[str]:
        return self.params.get("ic-element-id")

    @property
    def element_name(self) -> Optional[str]:
        return self.params.get("ic-element-name")

    @property
    def trigger_id(self) -> Optional[str]:
        return self.params.get("ic-trigger-id")

    @property
    def trigger_name(self) -> Optional[str]:
        return self.params.get("ic-trigger-name")

    @property
    def prompt_value(self) -> Optional[str]:
        return self.params.get("ic-prompt-value")


def _is_intercooler(self) -> bool:
    return self.is_ajax() and "x-ic-request" in self.headers


def _get_intercooler_data(self) -> IntercoolerData:

    if self.method in ("GET", "HEAD", "OPTIONS"):
        query_dict = self.GET
    elif self.method == "POST":
        query_dict = self.POST
    else:
        query_dict = QueryDict(self.body)

    return IntercoolerData(
        {
            k: query_dict[k]
            for k in query_dict
            if k in INTERCOOLER_PARAMS and k in query_dict
        }
    )


def _is_intercooler_target(self) -> bool:
    return self.is_intercooler() and self.intercooler_data.target


class IntercoolerRequestMiddleware:
    """
    Adds method `is_intercooler` to request instance if Intercooler
    headers are present and is an XHR request.

    Also adds property `intercooler_data` containing all info from
    Intercooler request parameters.

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
        request.intercooler_data = SimpleLazyObject(
            _get_intercooler_data.__get__(request)
        )
        return self.get_response(request)


class IntercoolerRedirectMiddleware:
    """
    If Intercooler headers present then will send a 200 OK instead
    of redirect with IC redirect header.

    IntercoolerRequestMiddleware must be installed in MIDDLEWARE.
    """

    def __init__(self, get_response: get_response_callable):
        self.get_response = get_response

    def ic_response(self, response: HttpResponse) -> HttpResponse:
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
