import pytest

from django.http import HttpRequest
from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView
from django.test.client import RequestFactory


from communikit.types import get_response_callable
from communikit.intercooler.views import IntercoolerTemplateMixin
from communikit.intercooler.middleware import IntercoolerRequestMiddleware


class MyView(IntercoolerTemplateMixin, TemplateView):
    template_name = "index.html"
    ic_template_name = "ic/index.html"


class TestIntercoolerTemplateMixin:
    def make_request(
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
        req = self.make_request(
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
        req = self.make_request(req_factory, get_response)
        my_view = MyView()
        my_view.request = req
        assert my_view.get_template_names() == ["index.html"]

    def test_if_ic_template_name_not_defined(
        self, req_factory: RequestFactory, get_response: get_response_callable
    ):
        req = self.make_request(
            req_factory,
            get_response,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_X_IC_REQUEST="true",
        )
        my_view = MyView()
        my_view.ic_template_name = None
        my_view.request = req

        with pytest.raises(ImproperlyConfigured):
            my_view.get_template_names()
