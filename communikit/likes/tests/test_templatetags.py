import pytest

from django.conf import settings

from communikit.content.models import Post
from communikit.likes.templatetags.likes_tags import has_liked

pytestmark = pytest.mark.django_db


class TestHasLiked:
    def test_has_liked(self, user: settings.AUTH_USER_MODEL, post: Post):
        post.like(user)
        assert has_liked(user, post)
