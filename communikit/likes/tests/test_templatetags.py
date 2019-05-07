import pytest

from django.conf import settings
from django.test.client import RequestFactory

from communikit.content.models import Post
from communikit.likes.middleware import LikesMiddleware
from communikit.likes.templatetags.likes_tags import has_liked
from communikit.types import HttpRequestResponse

pytestmark = pytest.mark.django_db


class TestHasLiked:
    def test_has_liked(
        self,
        user: settings.AUTH_USER_MODEL,
        post: Post,
        req_factory: RequestFactory,
        get_response: HttpRequestResponse,
    ):
        post.like(user)
        req = req_factory.get("/")
        req.user = user
        LikesMiddleware(get_response)(req)
        assert has_liked({"request": req}, post)
