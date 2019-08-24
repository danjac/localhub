from django.forms import Form
from django.test.client import RequestFactory

from localhub.core.templatetags.form_tags import simple_ajax_form
from localhub.core.templatetags.pagination_tags import pagination_url


class TestSimpleAjaxForm:
    def test_simple_ajax_form(self, req_factory: RequestFactory):
        class MyForm(Form):
            ...

        form = MyForm()
        req = req_factory.get("/some-action/")
        context = simple_ajax_form({"request": req}, form)
        assert context["action"] == "/some-action/"
        assert context["form"] == form


class TestPaginationUrl:
    def test_append_page_number_to_querystring(
        self, req_factory: RequestFactory
    ):

        req = req_factory.get("/search/", {"q": "test"})
        url = pagination_url({"request": req}, 5)
        assert url.startswith("/search/?")
        assert "q=test" in url
        assert "page=5" in url
