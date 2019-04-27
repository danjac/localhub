import pytest

from django.utils.encoding import force_str

from .factories import PostFactory

pytestmark = pytest.mark.django_db


class TestPostModel:
    def test_markdown(self):
        post = PostFactory(description="*testing*")
        assert force_str(post.markdown()) == "<p><em>testing</em></p>"

    def test_markdown_with_dangerous_tags(self):
        post = PostFactory(
            description="<script>alert('howdy');</script>"
        )
        assert (
            force_str(post.markdown())
            == "&lt;script&gt;alert('howdy');&lt;/script&gt;"  # noqa
        )
