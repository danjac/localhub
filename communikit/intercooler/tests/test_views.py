from django.http import HttpRequest
from django.test.client import RequestFactory
from django.views.generic import TemplateView

from communikit.intercooler.middleware import IntercoolerRequestMiddleware
from communikit.intercooler.views import (
    IntercoolerDeleteView,
    IntercoolerTemplateMixin,
)
from communikit.types import get_response_callable


class FakeDeletionObject:
    def delete(self):
        pass


class MyView(IntercoolerTemplateMixin, TemplateView):
    template_name = "index.html"
    ic_template_name = "ic/index.html"


class MyDeleteView(IntercoolerDeleteView):
    success_url = "/"

    def get_object(self):
        return FakeDeletionObject()


class TestIntercoolerDeleteView:
    def make_ic_request(
        self,
        req_factory: RequestFactory,
        get_response: get_response_callable,
        **headers
    ) -> HttpRequest:
        req = req_factory.delete("/", **headers)
        mw = IntercoolerRequestMiddleware(get_response)
        mw(req)
        return req

    def test_is_intercooler_target_id(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        req = self.make_ic_request(
            req_factory,
            get_response,
            data="ic-target-id=#posts",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_IC_REQUEST="true",
        )
        my_view = MyDeleteView()
        response = my_view.delete(req)
        assert "X-IC-Remove" in response

    def test_is_intercooler_no_target_id(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        req = self.make_ic_request(
            req_factory,
            get_response,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_IC_REQUEST="true",
        )
        my_view = MyDeleteView()
        response = my_view.delete(req)
        assert response["Location"] == "/"

    def test_is_not_intercooler(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        req = self.make_ic_request(req_factory, get_response)
        my_view = MyDeleteView()
        response = my_view.delete(req)
        assert response["Location"] == "/"


class TestIntercoolerTemplateMixin:
    def make_ic_request(
        self,
        req_factory: RequestFactory,
        get_response: get_response_callable,
        **headers
    ) -> HttpRequest:
        req = req_factory.get("/", **headers)
        mw = IntercoolerRequestMiddleware(get_response)
        mw(req)
        return req

    def test_is_intercooler(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        req = self.make_ic_request(
            req_factory,
            get_response,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_IC_REQUEST="true",
        )
        my_view = MyView()
        my_view.request = req
        assert my_view.get_template_names() == ["ic/index.html"]

    def test_is_not_intercooler(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        req = self.make_ic_request(req_factory, get_response)
        my_view = MyView()
        my_view.request = req
        assert my_view.get_template_names() == ["index.html"]

    def test_if_ic_template_name_not_defined(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        req = self.make_ic_request(
            req_factory,
            get_response,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_IC_REQUEST="true",
        )
        my_view = MyView()
        my_view.ic_template_name = None
        my_view.request = req
        assert my_view.get_template_names() == ["index.html"]
