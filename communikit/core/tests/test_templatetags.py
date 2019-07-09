from django.test.client import RequestFactory

from communikit.core.templatetags.pagination_tags import pagination_url


class TestPaginationUrl:
    def test_append_page_number_to_querystring(
        self, req_factory: RequestFactory
    ):

        req = req_factory.get("/search/", {"q": "test"})
        url = pagination_url({"request": req}, 5)
        assert url.startswith("/search/?")
        assert "q=test" in url
        assert "page=5" in url
