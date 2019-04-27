from django.test.client import RequestFactory

from communikit.types import get_response_callable
from communikit.intercooler.middleware import IntercoolerRequestMiddleware


class TestIntercoolerRequestMiddleware:
    def test_is_intercooler(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        mw = IntercoolerRequestMiddleware(get_response)
        req = req_factory.get(
            "/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_IC_REQUEST="true",
        )
        mw(req)
        assert req.is_intercooler()

    def test_is_intercooler_if_no_ic_headers(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        mw = IntercoolerRequestMiddleware(get_response)
        req = req_factory.get("/", HTTP_X_REQUESTED_WITH="XMLHttpRequest")
        mw(req)
        assert not req.is_intercooler()

    def test_is_intercooler_if_not_ajax(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        mw = IntercoolerRequestMiddleware(get_response)
        req = req_factory.get("/", HTTP_X_IC_REQUEST="true")
        mw(req)
        assert not req.is_intercooler()
