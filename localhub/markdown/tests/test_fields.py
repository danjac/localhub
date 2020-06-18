# Django
from django.utils.encoding import force_str

# Third Party Libraries
import pytest

# Localhub
# Social-BFG
from localhub.apps.posts.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestMarkdownField:
    def test_markdown(self):
        post = PostFactory(description="# test")
        assert force_str(post.description.markdown()) == "<h1>test</h1>"

    def test_extract_mentions(self):
        post = PostFactory(description="hello @danjac")
        assert "danjac" in post.description.extract_mentions()
