import pytest

from django.urls import reverse
from django.utils.encoding import force_str

from communikit.communities.models import Community
from communikit.content.models import Post
from communikit.content.tests.factories import PostFactory

pytestmark = pytest.mark.django_db


class TestPostModel:
    def test_markdown(self):
        post = Post(description="*testing*")
        assert force_str(post.markdown()) == "<p><em>testing</em></p>"

    def test_markdown_with_dangerous_tags(self):
        post = Post(description="<script>alert('howdy');</script>")
        assert (
            force_str(post.markdown())
            == "&lt;script&gt;alert('howdy');&lt;/script&gt;"
        )

    def test_get_absolute_url(self):
        post = PostFactory()
        assert post.get_absolute_url() == reverse(
            "content:detail", args=[post.id]
        )

    def test_get_permalink(self, community: Community):
        post = PostFactory(community=community)
        assert post.get_permalink() == f"http://testserver/post/{post.id}/"
