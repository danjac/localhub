import pytest

from django.conf import settings
from django.urls import reverse
from django.utils.encoding import force_str

from communikit.communities.models import Community
from communikit.content.models import Post
from communikit.content.tests.factories import PostFactory
from communikit.likes.models import Like

pytestmark = pytest.mark.django_db


class TestPostModel:
    def test_like(self, post: Post, user: settings.AUTH_USER_MODEL):
        assert post.like(user)
        assert Like.objects.count() == 1

    def test_unlike(self, post: Post, user: settings.AUTH_USER_MODEL):
        Like.objects.create(content_object=post, user=user)
        assert not post.like(user)
        assert Like.objects.count() == 0

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
