import pytest

from typing import Callable

from django.conf import settings
from django.contrib.auth.models import AnonymousUser

from communikit.content.models import Post
from communikit.content.tests.factories import PostFactory
from communikit.likes.models import Like

pytestmark = pytest.mark.django_db


class TestLikeModel:
    def test_has_liked_if_anonymous_user(self, post: Post):
        assert not Like.objects.user_has_liked(AnonymousUser(), post)

    def test_has_not_liked(self, post: Post, user: settings.AUTH_USER_MODEL):
        assert not Like.objects.user_has_liked(user, post)

    def test_has_liked(self, post: Post, user: settings.AUTH_USER_MODEL):
        Like.objects.create(user=user, content_object=post)
        assert Like.objects.user_has_liked(user, post)

    def test_cached_likes(
        self,
        user: settings.AUTH_USER_MODEL,
        django_assert_max_num_queries: Callable,
    ):
        PostFactory.create_batch(5)
        posts = list(Post.objects.all())
        with django_assert_max_num_queries(2):
            for post in posts:
                Like.objects.user_has_liked(user, post)
