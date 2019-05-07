import pytest

from typing import Callable

from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.test.client import RequestFactory

from communikit.content.models import Post
from communikit.content.tests.factories import PostFactory
from communikit.likes.middleware import LikesMiddleware
from communikit.types import HttpRequestResponse

pytestmark = pytest.mark.django_db


class TestLikeModel:
    def test_has_liked_if_anonymous_user(
        self,
        req_factory: RequestFactory,
        get_response: HttpRequestResponse,
        post: Post,
    ):
        mw = LikesMiddleware(get_response)
        req = req_factory.get("/")
        req.user = AnonymousUser()
        mw(req)
        assert not req.has_liked(post)

    def test_has_not_liked(
        self,
        req_factory: RequestFactory,
        get_response: HttpRequestResponse,
        post: Post,
        user: settings.AUTH_USER_MODEL,
    ):
        mw = LikesMiddleware(get_response)
        req = req_factory.get("/")
        req.user = user
        mw(req)
        assert not req.has_liked(post)

    def test_has_liked(
        self,
        req_factory: RequestFactory,
        get_response: HttpRequestResponse,
        post: Post,
        user: settings.AUTH_USER_MODEL,
    ):
        post.likes(user)
        mw = LikesMiddleware(get_response)
        req = req_factory.get("/")
        req.user = user
        mw(req)
        assert req.has_liked(post)

    def test_cached_likes(
        self,
        req_factory: RequestFactory,
        get_response: HttpRequestResponse,
        user: settings.AUTH_USER_MODEL,
        django_assert_max_num_queries: Callable,
    ):
        PostFactory.create_batch(5)
        posts = list(Post.objects.all())
        for post in posts:
            post.likes(user)

        req = req_factory.get("/")
        mw = LikesMiddleware(get_response)
        mw(req)
        req.user = user

        with django_assert_max_num_queries(2):
            for post in posts:
                req.has_liked(post)
